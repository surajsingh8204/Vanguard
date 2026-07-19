import hashlib
import json
import logging
import re
from collections import Counter
from typing import Any

from core.config.settings import (
    ANALYTICS_DIR,
    ARTIFACT_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    FINAL_RERANK_K,
    GLOBAL_RETRIEVAL_K,
    MIN_CHUNK_LENGTH,
    MIN_CLUSTER_SIZE,
    MIN_CONFIDENCE,
    MIN_SAMPLES,
    TOP_CLUSTERS,
    VECTORSTORE_DIR,
)
from core.embeddings.embedding_services import EmbeddingService
from core.vectorstore.faiss_store import VectorStore
from core.intelligence.rag_engine import RAGEngine
from core.intelligence.retrieval_reranker import RetrievalReranker

from core.clustering.hdbscan_cluster import HDBSCANClusterer
from core.clustering.subcluster import SubClusterer
from core.analytics.cluster_labeler import ClusterLabeler
from core.analytics.narrative.subcluster_labeler import SubclusterLabeler
from core.processing.document_purifier import DocumentPurifier
from core.analytics.narrative.timeline_engine import TimelineEngine
from core.analytics.evaluation.evaluation_engine import EvaluationEngine
from core.analytics.narrative.spike_detector import SpikeDetector
from core.analytics.narrative.evolution_engine import EvolutionEngine
from core.logger.evaluation_logger import EvaluationLogger
from core.analytics.graphs.topk_graph import TopKGraph
from core.analytics.graphs.graph_diagnostics import GraphDiagnostics
from core.analytics.graphs.community_detector import CommunityDetector
from core.analytics.graphs.centrality_analyzer import CentralityAnalyzer
from core.analytics.narrative.narrative_statistics import NarrativeStatistics
from core.analytics.influence_engine import InfluenceEngine
from core.analytics.graphs.influence_mapper import InfluenceMapper
from core.analytics.narrative.emerging_narrative_detector import EmergingNarrativeDetector
from core.analytics.narrative.forecast_engine import ForecastEngine
from core.analytics.narrative.early_warning_engine import EarlyWarningEngine
from core.analytics.evaluation.forecast_evaluator import ForecastEvaluator
from core.analytics.evaluation.correlation_evaluator import CorrelationEvaluator
from core.analytics.evaluation.label_audit import LabelAudit
from core.processing.data_quality_firewall import DataQualityFirewall
from core.outputs.reports.intelligence_brief import (
    IntelligenceBriefGenerator
)
from core.outputs.reports.impact_analysis import (
    ImpactAnalyzer
)
from core.outputs.reports.executive_brief import (
    ExecutiveBriefGenerator
)
from core.intelligence.strategic_context_builder import (
    StrategicContextBuilder
)

from core.utils.artifact_manager import ArtifactManager

logger = logging.getLogger(__name__)

class AIPipeline:

    def __init__(self, embedding_service=None):

        print("Loading embedding model...")
        self.embedding_service = embedding_service or EmbeddingService()

        print("Initializing RAG engine...")
        self.rag = RAGEngine()

        self.vector_store = None
        self.evaluation_logger = EvaluationLogger()
        self.timeline = None
        self.forecasts = None
        self.early_warnings = None
        self.influence_scores = None
        self.executive_brief = None
        self.strategic_context = None
        
    # ---------------------------------------------------
    # TEXT CHUNKING
    # ---------------------------------------------------

    def chunk_text(self, text, chunk_size=CHUNK_SIZE):

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):

            chunk = " ".join(words[i:i + chunk_size])

            if len(chunk.strip()) > MIN_CHUNK_LENGTH:
                chunks.append(chunk)

        return chunks

    # ---------------------------------------------------
    # BUILD VECTOR DATABASE
    # ---------------------------------------------------

    def build_vector_db(
        self,
        articles,
        force_rebuild=False,
        dataset_path="data_lake/processed/enriched_articles.json",
    ):

        print("Building vector database...")

        artifact_manager = ArtifactManager()

        with open(dataset_path, "rb") as f:
            current_hash = hashlib.md5(
                f.read()
            ).hexdigest()

        build_info = artifact_manager.load_json(
            f"{ARTIFACT_DIR}/build_info.json"
        )

        use_cache = (
            not force_rebuild
            and build_info is not None
            and build_info.get("dataset_hash") == current_hash
            and build_info.get("retrieval_quality_version") == 2
            and artifact_manager.exists(f"{VECTORSTORE_DIR}/faiss.index")
        )

        if use_cache:

            print("\n✅ Dataset unchanged.")
            print("Loading existing artifacts...\n")

            self.clustered_chunks = artifact_manager.load_json(
                f"{ARTIFACT_DIR}/clustered_chunks.json"
            )

            self.cluster_labels = artifact_manager.load_json(
                f"{ARTIFACT_DIR}/cluster_labels.json"
            )

            self.subcluster_labels = artifact_manager.load_json(
                f"{ARTIFACT_DIR}/subcluster_labels.json"
            )

            self.cluster_groups = artifact_manager.load_json(
                f"{ARTIFACT_DIR}/cluster_groups.json"
            )

            self.cluster_labels = {
                int(key): value
                for key, value in self.cluster_labels.items()
            }

            self.subcluster_labels = {
                int(cluster_id): {
                    int(subcluster_id): label
                    for subcluster_id, label in subclusters.items()
                }
                for cluster_id, subclusters in self.subcluster_labels.items()
            }

            self.cluster_groups = {
                int(cluster_id): items
                for cluster_id, items in self.cluster_groups.items()
            }

            self.vector_store = VectorStore.load(
                VECTORSTORE_DIR
            )

            print("✅ Vanguard loaded from core.artifacts.")
            return

        all_chunks = []
        purifier = DocumentPurifier()
        firewall = DataQualityFirewall()
        existing_hashes = set()

        for article in articles:

            if not article.get("content"):
                continue
            
            #---------------------------------------------------
            # PURIFY DOCUMENT
            #---------------------------------------------------
            cleaned = purifier.clean(article["content"])

            #---------------------------------------------------
            # FIREWALL CHECK
            #---------------------------------------------------
            valid, reason = firewall.validate(
                cleaned,
                existing_hashes
            )

            if not valid:
                continue

            #---------------------------------------------------
            # QUALITY CHECK
            #---------------------------------------------------
            if not purifier.is_valid(cleaned):
                continue
            
            #---------------------------------------------------
            # CHUNKING
            #---------------------------------------------------
            chunks = self.chunk_text(cleaned)
            metadata = self._prepare_article_metadata(article)
            for chunk in chunks:

                chunk_record = {
                    "text": chunk,
                    "title": metadata["title"],
                    "source": metadata["source"],
                    "date": metadata["date"],
                    "country": metadata["country"],
                    "language": metadata["language"],
                    "topic": metadata["topic"],
                }
                all_chunks.append(self._validate_chunk_metadata(chunk_record))

        print("Total chunks:", len(all_chunks))

        if len(all_chunks) == 0:
            raise ValueError("No valid chunks found after document purification.")

        # ---------------------------------------------------
        # EMBEDDINGS
        # ---------------------------------------------------

        texts = [x["text"] for x in all_chunks]

        embeddings = self.embedding_service.embed(texts)

        # ---------------------------------------------------
        # MAIN CLUSTERING
        # ---------------------------------------------------

        print("Running main narrative clustering...")

        labeler = ClusterLabeler()

        self.cluster_labels = {}
        self.initial_cluster_labels = {}

        clusterer = HDBSCANClusterer(
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES
        )

        labels = clusterer.cluster(embeddings)


        


        

        # ---------------------------------------------------
        # GROUP BY MAIN CLUSTER
        # ---------------------------------------------------

        cluster_groups = {}

        for i, label in enumerate(labels):

            if label == -1:
                continue

            if label not in cluster_groups:
                cluster_groups[label] = []

            cluster_groups[label].append({
                "text": all_chunks[i]["text"],
                "embedding": embeddings[i],
                "date": all_chunks[i]["date"],
                "title": all_chunks[i].get("title"),
                "source": all_chunks[i].get("source"),
                "country": all_chunks[i].get("country"),
                "language": all_chunks[i].get("language"),
                "topic": all_chunks[i].get("topic"),
            })

        print("Main clusters found:", len(cluster_groups))
        self.cluster_groups = cluster_groups
        
        # ---------------------------------------------------
        # SUBCLUSTERING
        # ---------------------------------------------------

        print("Running hierarchical sub-clustering...")

        subclusterer = SubClusterer()

        clustered_chunks = []
        filtered_embeddings = []

        for main_cluster, items in cluster_groups.items():

            # ---------------------------------------------------
            # GENERATE MAIN CLUSTER LABEL
            # ---------------------------------------------------

            cluster_texts = items

            cluster_label = labeler.generate_label(
                cluster_texts
                )

            self.initial_cluster_labels[
                int(main_cluster)
            ] = cluster_label


            if not hasattr(self, "subcluster_labels"):
                self.subcluster_labels = {}

            self.subcluster_labels[int(main_cluster)] = {}

            cluster_embeddings = [x["embedding"] for x in items]

            # small clusters skip subclustering
            if len(cluster_embeddings) < 5:

                small_cluster_texts = [

                    x

                    for x in items

                ]

                label = (

                    labeler.generate_label(

                        small_cluster_texts

                    )

                )

                self.subcluster_labels[
                    int(main_cluster)
                ][0] = label

                for item in items:

                    clustered_chunks.append({
                        "text": item["text"],
                        "cluster": int(main_cluster),
                        "subcluster": 0,
                        "topic": label,
                        "title": item.get("title"),
                        "source": item.get("source"),
                        "date": item.get("date"),
                        "country": item.get("country"),
                        "language": item.get("language"),
                    })

                    filtered_embeddings.append(item["embedding"])

                continue

            # ---------------------------------------------
            # RUN SUBCLUSTERING
            # ---------------------------------------------

            sub_labels = subclusterer.cluster(
                cluster_embeddings
            )

            # ---------------------------------------------
            # HANDLE NOISE-ONLY SUBCLUSTERS
            # ---------------------------------------------

            valid_subclusters = [

                x for x in sub_labels

                if x != -1

            ]

            if len(valid_subclusters) == 0:

                sub_labels = [

                    0

                    for _ in sub_labels

                ]

                print(
                    f"Cluster {main_cluster} "
                    f"had only noise subclusters."
                )

            print("\n" + "=" * 50)

            print(
                f"MAIN CLUSTER {main_cluster}"
            )

            print(
                "UNIQUE SUBCLUSTER IDS:",
                set(sub_labels)
            )

            print("=" * 50)

            from collections import defaultdict

            subcluster_groups = defaultdict(list)

            for idx, sub_id in enumerate(sub_labels):

                if sub_id == -1:
                    continue

                subcluster_groups[sub_id].append(items[idx])

            # ---------------------------------------------
            # GENERATE LABELS
            # ---------------------------------------------

            for sub_id, texts in (

                subcluster_groups.items()

            ):

                label = (

                    labeler.generate_label(texts)

                )

                self.subcluster_labels[
                    int(main_cluster)
                ][
                    int(sub_id)
                ] = label

            for idx, item in enumerate(items):

                subcluster_label = self.subcluster_labels[
                    int(main_cluster)
                ].get(
                    int(sub_labels[idx]),
                    cluster_label,
                )

                clustered_chunks.append({
                    "text": item["text"],
                    "cluster": int(main_cluster),
                    "subcluster": int(sub_labels[idx]),
                    "topic": subcluster_label or cluster_label,
                    "title": item.get("title"),
                    "source": item.get("source"),
                    "date": item.get("date"),
                    "country": item.get("country"),
                    "language": item.get("language"),
                })

                filtered_embeddings.append(item["embedding"])

        print("\n📌 SAMPLE SUBCLUSTER LABELS\n")

        shown = 0

        for cluster_id, subs in self.subcluster_labels.items():

            print(
                f"\nMain Cluster {cluster_id}"
            )

            for sub_id, label in subs.items():

                print(
                    f"   Subcluster {sub_id}: {label}"
                )

            shown += 1

            if shown >= 5:
                break

        print("\n🔄 Rebuilding Main Cluster Labels...\n")

        for cluster_id, subclusters in self.subcluster_labels.items():

            sub_labels = list(
                subclusters.values()
            )

            if len(sub_labels) == 0:

                self.cluster_labels[
                    cluster_id
                ] = self.initial_cluster_labels.get(
                    cluster_id,
                    "Unknown Narrative"
                )

                continue

            try:

                rebuilt_label = (
                    labeler.generate_label(
                        sub_labels
                    )
                )

            except Exception:

                rebuilt_label = (
                    self.initial_cluster_labels.get(
                        cluster_id,
                        "Unknown Narrative"
                    )
                )

            self.cluster_labels[cluster_id] = rebuilt_label

            print(
                f"Cluster {cluster_id}"
            )

            print(
                f"Old: {self.initial_cluster_labels.get(cluster_id)}"
            )

            print(
                f"New: {rebuilt_label}"
            )

            print("-" * 40)

        print("After noise removal:", len(clustered_chunks))

        # ---------------------------------------------------
        # SUBCLUSTER LABELING SANITY CHECK
        # ---------------------------------------------------

        print(
            "Total Main Clusters:",
            len(self.subcluster_labels)
        )

        total_subs = sum(
            len(v)
            for v in self.subcluster_labels.values()
        )

        print(
            "Total Subclusters:",
            total_subs
        )

        self.evaluation_logger.save(
            "subcluster_labels",
            self.subcluster_labels
        )

        # Save for analytics modules
        self.clustered_chunks = [
            self._validate_clustered_chunk_metadata(
                chunk,
                self.cluster_labels.get(chunk["cluster"]),
                self.subcluster_labels.get(chunk["cluster"], {}).get(chunk["subcluster"]),
            )
            for chunk in clustered_chunks
        ]

        if len(filtered_embeddings) == 0:
            raise ValueError("No clustered chunks found after noise removal.")
        
        # ---------------------------------------------------
        # VECTOR DATABASE
        # ---------------------------------------------------

        dimension = len(filtered_embeddings[0])

        self.vector_store = VectorStore(dimension)

        self.vector_store.add(
            filtered_embeddings,
            self.clustered_chunks
        )

        self.vector_store.save(
            VECTORSTORE_DIR
        )

        self.clustered_chunks = self.clustered_chunks

        artifact_manager = ArtifactManager()

        artifact_manager.save_json(

            f"{ARTIFACT_DIR}/clustered_chunks.json",

            self.clustered_chunks

        )

        artifact_manager.save_json(

            f"{ARTIFACT_DIR}/cluster_labels.json",

            self.cluster_labels

        )

        artifact_manager.save_json(

            f"{ARTIFACT_DIR}/subcluster_labels.json",

            self.subcluster_labels

        )

        artifact_manager.save_json(

            f"{ARTIFACT_DIR}/cluster_groups.json",

            self.cluster_groups

        )

        print(
            "\n✅ Clustering artifacts saved."
        )

        with open(dataset_path, "rb") as f:
            dataset_hash = hashlib.md5(
                f.read()
            ).hexdigest()

        build_info = {
            "dataset_hash": dataset_hash,
            "embedding_model": EMBEDDING_MODEL,
            "num_chunks": len(self.clustered_chunks),
            "retrieval_quality_version": 2,
        }

        artifact_manager.save_json(
            f"{ARTIFACT_DIR}/build_info.json",
            build_info
        )

        print("✅ Build information saved.")

        firewall.print_report()

        print(
            "Vector DB built with",
            len(self.clustered_chunks),
            "clean chunks"
        )

    # ---------------------------------------------------
    # QUERY SYSTEM
    # ---------------------------------------------------

    def query(self, question):
        self.query_embedding = self.embedding_service.embed([question])[0]
        query_embedding = self.embedding_service.embed([question])[0]

        # ---------------------------------------------------
        # GLOBAL SEARCH
        # ---------------------------------------------------

        initial_results = self.vector_store.search(
            query_embedding,
            k=GLOBAL_RETRIEVAL_K
        )

        clusters = [r["cluster"] for r in initial_results]

        top_clusters = [
            c[0]
            for c in Counter(clusters).most_common(TOP_CLUSTERS)
        ]

        print("\n🎯 Top Narrative Clusters:\n")

        for cid in top_clusters:

            label = self.cluster_labels.get(
                cid,
                "Unknown"
            )

            print(
                f"🧠 {label}"
            )

            subtopics = list(

                self.subcluster_labels
                    .get(cid, {})
                    .values()

            )[:3]

            for topic in subtopics:

                print(
                    f"   • {topic}"
                )

            print()

        # ---------------------------------------------------
        # CLUSTER-LEVEL SEARCH
        # ---------------------------------------------------

        all_results = []

        for cluster_id in top_clusters:

            cluster_results = self.vector_store.search_in_cluster(
                query_embedding,
                cluster_id,
                k=GLOBAL_RETRIEVAL_K // TOP_CLUSTERS
            )

            all_results.extend(cluster_results)

        # ---------------------------------------------------
        # GLOBAL RERANK
        # ---------------------------------------------------

        reranker = RetrievalReranker()
        enriched_results = [
            self._enrich_result_metadata(result)
            for result in all_results
        ]
        results = reranker.rerank(
            enriched_results,
            query=question,
            max_per_subcluster=2,
            top_k=FINAL_RERANK_K
        )
        # ---------------------------------------------
        # RETRIEVAL CONFIDENCE CHECK
        # ---------------------------------------------
        results = [
            self._apply_confidence(result, top_clusters)
            for result in results
        ]
        scores = [r["confidence_score"] for r in results]

        if not scores:
            return (
                "Insufficient narrative evidence found in the current media corpus.",
                {
                    "question": question,
                    "max_score": 0.0,
                    "avg_score": 0.0,
                    "min_score": 0.0,
                },
            )

        avg_score = sum(scores) / len(scores)

        if avg_score >= 0.85:

            confidence_level = "Very High"

        elif avg_score >= 0.70:

            confidence_level = "High"

        elif avg_score >= 0.50:

            confidence_level = "Medium"

        else:

            confidence_level = "Low"

        print(
            f"\n🎯 Retrieval Confidence: "
            f"{confidence_level}"
        )

        print(
            f"Score: {avg_score:.4f}"
        )

        retrieval_stats = {

            "question": question,

            "max_score": max(scores),

            "avg_score": avg_score,

            "min_score": min(scores),
        }

        if avg_score < MIN_CONFIDENCE:

            return (
                "Insufficient narrative evidence found "
                "in the current media corpus.",
                retrieval_stats
            )

        print("\n📊 Retrieval Stats")

        print(
            f"Max Score: {max(scores):.4f}"
        )

        print(
            f"Average Score: {avg_score:.4f}"
        )

        print(
            f"Min Score: {min(scores):.4f}"
        )

        # ---------------------------------------------------
        # DISPLAY
        # ---------------------------------------------------

        print(
            "\n🔍 Supporting Narrative Evidence:\n"
        )

        for r in results:

            cluster_id = r["cluster"]

            subcluster_id = r.get(
                "subcluster",
                0
            )

            cluster_label = self.cluster_labels.get(
                cluster_id,
                "Unknown"
            )

            subcluster_label = (
                self.subcluster_labels
                    .get(cluster_id, {})
                    .get(
                        subcluster_id,
                        "Unknown"
                    )
            )

            print(
                f"📂 Narrative Domain: "
                f"{cluster_label}"
            )

            print(
                f"🎯 Specific Topic: "
                f"{subcluster_label}"
            )

            print(
                f"📰 Source: "
                f"{r.get('source', 'Unknown')}"
            )

            print(
                f"📅 Date: "
                f"{r.get('date', 'Unknown')}"
            )

            print(
                f"📊 Confidence: "
                f"{r['confidence_level']} ({r['confidence_score']:.4f})"
            )

            print(
                f"🧩 Cluster: "
                f"{cluster_id}"
            )

            print(
                f"🧷 Subcluster: "
                f"{subcluster_id}"
            )

            print(r["text"][:200])

            print("-" * 50)

        # ---------------------------------------------------
        # CONTEXT BUILDING
        # ---------------------------------------------------

        retrieval_context = "\n\n".join(

            r["text"]

            for r in results

        )

        # ---------------------------------------------------
        # GENERATE RESPONSE
        # ---------------------------------------------------

        answer = self.rag.generate(
            retrieval_context,
            question,
            self.strategic_context
        )

        return answer, retrieval_stats

    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------

    def run_analytics(self, force_rebuild=False):
        from datetime import datetime

        artifact_manager = ArtifactManager()
        evaluation_logger = EvaluationLogger()

        def save_artifact(relative_path, payload):
            try:
                artifact_manager.save_json(
                    f"{ARTIFACT_DIR}/{relative_path}",
                    payload
                )
                logger.info("Saved %s", relative_path)
            except Exception:
                logger.exception("Failed to save %s", relative_path)

        if not force_rebuild and artifact_manager.analytics_exist():

            self.timeline = artifact_manager.load_json(
                f"{ANALYTICS_DIR}/timeline.json"
            )

            self.forecasts = artifact_manager.load_json(
                f"{ANALYTICS_DIR}/forecasts.json"
            )

            self.early_warnings = artifact_manager.load_json(
                f"{ANALYTICS_DIR}/early_warnings.json"
            )

            self.influence_scores = artifact_manager.load_json(
                f"{ANALYTICS_DIR}/influence_scores.json"
            )

            self.executive_brief = artifact_manager.load_json(
                f"{ANALYTICS_DIR}/executive_brief.json"
            )

            self.strategic_context = artifact_manager.load_json(
                f"{ANALYTICS_DIR}/strategic_context.json"
            )

            print("✅ Using cached analytics.")
            return

        save_artifact("narrative/clusters.json", self.cluster_groups)
        save_artifact("narrative/cluster_labels.json", self.cluster_labels)
        save_artifact(
            "narrative/subcluster_labels.json",
            self.subcluster_labels
        )

        timeline_engine = TimelineEngine()
        timeline_engine.build(
            self.clustered_chunks,
            self.cluster_labels
        )
        timeline_engine.display()

        self.timeline = timeline_engine.timeline
        save_artifact("narrative/timeline.json", timeline_engine.timeline)

        # ---------------------------------------------------
        # SPIKE DETECTION
        # ---------------------------------------------------

        spike_detector = SpikeDetector()

        spikes = spike_detector.detect(
            timeline_engine.timeline
        )

        spike_detector.display(spikes)
        save_artifact("narrative/spikes.json", spikes)

        evaluation_logger.save(
            "spike_report",
            spikes
        )

        # ---------------------------------------------------
        # EMERGING NARRATIVE DETECTION
        #---------------------------------------------------
        emerging_detector = EmergingNarrativeDetector()

        emerging_narratives = emerging_detector.detect(
            spikes
        )
        emerging_detector.display(
            emerging_narratives
        )
        save_artifact("narrative/emerging.json", emerging_narratives)
        evaluation_logger.save(
            "emerging_narratives",
            emerging_narratives
        )

        #---------------------------------------------------
        #NARRATIVE EVOLUTION
        #---------------------------------------------------
        evolution_engine = EvolutionEngine()
        temporal_clusters = evolution_engine.build_temporal_clusters(
            self.clustered_chunks,
            self.cluster_labels
        )
        evolution_report = evolution_engine.detect_evolution(
            temporal_clusters
        )
        evolution_engine.display(evolution_report)
        save_artifact("narrative/evolution.json", evolution_report)

        evaluation_logger.save(
            "evolution_report",
            evolution_report
        )

        # ---------------------------------------------------
        # EVALUATION
        # ---------------------------------------------------

        evaluator = EvaluationEngine()

        coherence = evaluator.cluster_coherence(
            self.cluster_groups
        )

        separation = evaluator.cluster_separation(
            self.cluster_groups
        )

        purity = evaluator.narrative_purity(
            self.cluster_groups
        )

        evaluator.display_report(
            coherence,
            separation,
            purity,
            self.cluster_labels
        )

        save_artifact("evaluation/coherence.json", coherence)
        save_artifact("evaluation/purity.json", purity)

        evaluation_logger.save(
            "coherence_scores",
            coherence
        )

        evaluation_logger.save(
            "purity_scores",
            purity
        )

        evaluation_logger.save(
            "cluster_labels",
            self.cluster_labels
        )

        evaluation_logger.save(
            "timeline_report",
            timeline_engine.timeline
        )

        save_artifact("analytics/timeline.json", timeline_engine.timeline)

        print("✅ Timeline saved.")

        # ---------------------------------------------------
        # LABEL AUDIT
        # ---------------------------------------------------

        audit_engine = LabelAudit()

        audit_report = (

            audit_engine.analyze(

                self.clustered_chunks,

                self.cluster_labels,

                self.subcluster_labels

            )

        )

        audit_engine.display(
            audit_report
        )

        save_artifact("evaluation/label_audit.json", audit_report)

        evaluation_logger.save(
            "label_audit",
            audit_report
        )

        # ---------------------------------------------------
        # NARRATIVE GRAPH
        # ---------------------------------------------------

        graph_engine = TopKGraph(k=3, min_similarity=MIN_CONFIDENCE)

        graph = graph_engine.build(

            self.cluster_groups,

            self.cluster_labels
        )

        save_artifact(
            "graphs/graph_summary.json",
            {
                "node_count": graph.number_of_nodes(),
                "edge_count": graph.number_of_edges(),
            }
        )
        save_artifact(
            "graphs/nodes.json",
            [
                {
                    "id": node,
                    **dict(attributes)
                }
                for node, attributes in graph.nodes(data=True)
            ]
        )
        save_artifact(
            "graphs/edges.json",
            [
                {
                    "source": source,
                    "target": target,
                    **dict(attributes)
                }
                for source, target, attributes in graph.edges(data=True)
            ]
        )

        graph_engine.display_summary()

        community_detector = CommunityDetector()

        communities = community_detector.detect(
            graph
        )
        save_artifact("graphs/communities.json", communities)

        community_detector.display(
            communities,
            graph
        )

        centrality = CentralityAnalyzer()

        centrality_results = centrality.analyze(
            graph
        )
        save_artifact("graphs/centrality.json", centrality_results)

        centrality.display(
            graph,
            centrality_results
        )

        stats_engine = NarrativeStatistics()

        narrative_stats = stats_engine.generate(
            self.clustered_chunks,
            self.cluster_labels
        )
        save_artifact("narrative/statistics.json", narrative_stats)
        save_artifact(
            "narrative/sentiment.json",
            {
                "status": "not_computed"
            }
        )

        stats_engine.display(
            narrative_stats
        )

        influence_engine = InfluenceEngine()

        influence_scores = (

            influence_engine.calculate(

                narrative_stats,

                centrality_results
            )
        )
        save_artifact("graphs/influencers.json", influence_scores)

        influence_engine.display(
            influence_scores
        )

        self.influence_scores = influence_scores

        save_artifact("analytics/influence_scores.json", influence_scores)

        print("✅ Influence scores saved.")

        mapper = InfluenceMapper()

        mappings = mapper.generate(
            graph,
            influence_scores
        )

        mapper.display(
            mappings
        )
        save_artifact("graphs/influence_mappings.json", mappings)

        diagnostics_engine = GraphDiagnostics()

        diagnostics = diagnostics_engine.analyze(

            self.cluster_groups,

            self.cluster_labels
        )

        diagnostics_engine.display(diagnostics)
        save_artifact("graphs/graph_diagnostics.json", diagnostics)
        evaluation_logger.save(
            "graph_diagnostics",
            diagnostics
        )

        # ---------------------------------------------------
        # NARRATIVE FORECASTING
        # ---------------------------------------------------

        forecast_engine = ForecastEngine()

        forecasts = forecast_engine.forecast(

            timeline_engine.timeline,

            influence_scores,

            emerging_narratives

        )

        forecast_engine.display(
            forecasts
        )
        save_artifact("narrative/forecasts.json", forecasts)

        evaluation_logger.save(
            "forecast_report",
            forecasts
        )

        self.forecasts = forecasts

        save_artifact("analytics/forecasts.json", forecasts)

        print("✅ Forecasts saved.")

        # ---------------------------------------------------
        # FORECAST EVALUATION
        # ---------------------------------------------------

        baseline_forecasts = (

            forecast_engine.baseline_forecast(

                timeline_engine.timeline

            )

        )

        evaluator = ForecastEvaluator()

        evaluation_results = (

            evaluator.evaluate(

                timeline_engine.timeline,

                baseline_forecasts,

                forecasts

            )

        )

        evaluator.display(

            evaluation_results
        )

        save_artifact(
            "evaluation/forecast_evaluation.json",
            evaluation_results
        )

        evaluation_logger.save(

            "forecast_evaluation",

            evaluation_results

        )

        # ---------------------------------------------------
        # EARLY WARNING SYSTEM
        # ---------------------------------------------------

        warning_engine = EarlyWarningEngine()

        warnings = warning_engine.generate(
            forecasts
        )

        warning_engine.display(
            warnings
        )

        self.early_warnings = warnings

        save_artifact("narrative/early_warnings.json", warnings)
        save_artifact("analytics/early_warnings.json", warnings)

        print("✅ Early warnings saved.")

        evaluation_logger.save(
            "early_warning_report",
            warnings
        )

        # ---------------------------------------------------
        # INTELLIGENCE BRIEFING
        # ---------------------------------------------------

        brief_generator = (
            IntelligenceBriefGenerator()
        )

        briefs = (

            brief_generator.generate(

                forecasts,

                influence_scores,

                warnings,

                graph

            )

        )

        brief_generator.display(
            briefs
        )

        save_artifact("metadata/intelligence_briefs.json", briefs)

        evaluation_logger.save(
            "intelligence_briefs",
            briefs
        )

        # ---------------------------------------------------
        # IMPACT ANALYSIS
        # ---------------------------------------------------

        impact_analyzer = ImpactAnalyzer()

        impact_reports = (

            impact_analyzer.generate(

                influence_scores,

                graph

            )

        )

        impact_analyzer.display(
            impact_reports
        )

        save_artifact("metadata/impact_reports.json", impact_reports)

        # ---------------------------------------------------
        # EXECUTIVE BRIEF
        # ---------------------------------------------------

        executive_generator = (

            ExecutiveBriefGenerator()

        )

        executive_brief = (

            executive_generator.generate(

                forecasts,

                warnings,

                influence_scores,

                impact_reports

            )

        )

        executive_generator.display(
            executive_brief
        )

        save_artifact("metadata/executive_brief.json", executive_brief)

        evaluation_logger.save(

            "executive_brief",

            executive_brief

        )

        self.executive_brief = executive_brief

        save_artifact("analytics/executive_brief.json", executive_brief)

        self.strategic_context = (

            StrategicContextBuilder()
            .build(

                forecasts,

                warnings,

                influence_scores,

                impact_reports

            )

        )

        save_artifact("metadata/strategic_context.json", self.strategic_context)
        save_artifact("analytics/strategic_context.json", self.strategic_context)

        # ---------------------------------------------------
        # CORRELATION EVALUATION
        # ---------------------------------------------------

        corr_evaluator = (

            CorrelationEvaluator()

        )

        corr_results = (

            corr_evaluator.evaluate(

                timeline_engine.timeline,

                baseline_forecasts,

                forecasts

            )

        )

        corr_evaluator.display(

            corr_results
        )

        save_artifact("evaluation/correlation.json", corr_results)

        evaluation_logger.save(

            "correlation_evaluation",

            corr_results

        )

        # ---------------------------------------------------
        # GRAPH DIAGNOSTICS
        # ---------------------------------------------------

        diagnostics_engine = GraphDiagnostics()

        diagnostics = diagnostics_engine.analyze(

            self.cluster_groups,

            self.cluster_labels
        )

        diagnostics_engine.display(diagnostics)
        save_artifact("graphs/graph_diagnostics.json", diagnostics)
        evaluation_logger.save(
            "graph_diagnostics",
            diagnostics
        )

        pipeline_status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "documents_processed": len(getattr(self, "clustered_chunks", [])),
            "cluster_count": len(getattr(self, "cluster_groups", {})),
            "subcluster_count": sum(
                len(subclusters)
                for subclusters in getattr(self, "subcluster_labels", {}).values()
            ),
            "embedding_model": EMBEDDING_MODEL,
            "vector_index_size": len(getattr(self.vector_store, "texts", []))
            if self.vector_store is not None else 0,
            "pipeline_version": "2",
            "status": "completed"
        }

        save_artifact("metadata/pipeline_status.json", pipeline_status)
    
    def initialize(self):
        print("Loading processed data...")

        with open(
            "data_lake/processed/enriched_articles.json",
            "r",
            encoding="utf-8"
        ) as f:
            articles = json.load(f)

        self.build_vector_db(articles)
        self.run_analytics(force_rebuild=False)

        print("✅ Vanguard Intelligence Ready")

    def run(self):

        self.initialize()

        print("Ready for queries!")

        while True:

            q = input("Ask a question (or 'exit'): ")

            if q.lower() == "exit":
                break

            response, retrieval_stats = self.query(q)

            print("\n🧠 Intelligence Report:\n")
            print(response)
            print("\n" + "=" * 60 + "\n")

    def _prepare_article_metadata(self, article: dict[str, Any]) -> dict[str, str]:
        title = self._clean_metadata_value(article.get("title"))
        source = self._clean_metadata_value(article.get("source"))
        date = self._clean_metadata_value(article.get("formatted_date") or article.get("date"))
        country = self._clean_metadata_value(article.get("country"))
        language = self._clean_metadata_value(article.get("language")) or "English"
        topic = self._clean_metadata_value(article.get("topic")) or title or source

        return {
            "title": title or "Untitled Article",
            "source": source or "Unknown Source",
            "date": date or "Unknown Date",
            "country": country or "Unknown Country",
            "language": language,
            "topic": topic or "General Coverage",
        }

    def _validate_chunk_metadata(self, chunk: dict[str, Any]) -> dict[str, Any]:
        validated = dict(chunk)
        validated["title"] = self._clean_metadata_value(validated.get("title")) or "Untitled Article"
        validated["source"] = self._clean_metadata_value(validated.get("source")) or "Unknown Source"
        validated["date"] = self._clean_metadata_value(validated.get("date")) or "Unknown Date"
        validated["country"] = self._clean_metadata_value(validated.get("country")) or "Unknown Country"
        validated["language"] = self._clean_metadata_value(validated.get("language")) or "English"
        validated["topic"] = (
            self._clean_metadata_value(validated.get("topic"))
            or validated["title"]
            or validated["source"]
            or "General Coverage"
        )
        return validated

    def _validate_clustered_chunk_metadata(
        self,
        chunk: dict[str, Any],
        cluster_label: str | None,
        subcluster_label: str | None,
    ) -> dict[str, Any]:
        validated = self._validate_chunk_metadata(chunk)
        validated["cluster"] = int(validated.get("cluster", -1))
        validated["subcluster"] = int(validated.get("subcluster", 0))
        validated["topic"] = (
            self._clean_metadata_value(subcluster_label)
            or self._clean_metadata_value(validated.get("topic"))
            or self._clean_metadata_value(cluster_label)
            or validated["title"]
        )
        return validated

    def _clean_metadata_value(self, value: Any) -> str:
        if value is None:
            return ""
        cleaned = str(value).strip()
        if not cleaned or cleaned.lower() in {"unknown", "none", "null"}:
            return ""
        return cleaned

    def _enrich_result_metadata(self, result: dict[str, Any]) -> dict[str, Any]:
        for item in getattr(self.vector_store, "texts", []):
            if (
                item.get("text") == result.get("text")
                and item.get("cluster") == result.get("cluster")
                and item.get("subcluster", 0) == result.get("subcluster", 0)
            ):
                enriched = dict(item)
                enriched["score"] = result.get("score", 0.0)
                enriched["topic"] = (
                    self._clean_metadata_value(item.get("topic"))
                    or self.subcluster_labels.get(result.get("cluster"), {}).get(result.get("subcluster", 0))
                    or self.cluster_labels.get(result.get("cluster"))
                    or item.get("title")
                    or "General Coverage"
                )
                return self._validate_chunk_metadata(enriched)
        return self._validate_chunk_metadata(result)

    def _apply_confidence(
        self,
        result: dict[str, Any],
        top_clusters: list[int],
    ) -> dict[str, Any]:
        metadata_fields = ("title", "source", "date", "country", "language", "topic")
        metadata_consistency = sum(
            1 for field in metadata_fields if self._clean_metadata_value(result.get(field))
        ) / len(metadata_fields)

        cluster_consistency = 0.0
        if result.get("cluster") in top_clusters:
            cluster_consistency += 0.7
        if self._clean_metadata_value(result.get("topic")):
            cluster_consistency += 0.3

        confidence_score = (
            (0.40 * float(result.get("vector_similarity", 0.0)))
            + (0.25 * float(result.get("reranker_score", 0.0)))
            + (0.20 * metadata_consistency)
            + (0.15 * cluster_consistency)
        )

        if confidence_score >= 0.85:
            confidence_level = "Very High"
        elif confidence_score >= 0.70:
            confidence_level = "High"
        elif confidence_score >= 0.50:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        enriched = dict(result)
        enriched["confidence_score"] = confidence_score
        enriched["confidence_level"] = confidence_level
        return enriched


if __name__ == "__main__":
    AIPipeline().run()
