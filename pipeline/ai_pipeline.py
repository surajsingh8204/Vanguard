import json
from collections import Counter

from embeddings.embedding_services import EmbeddingService
from vectorstore.faiss_store import VectorStore
from intelligence.rag_engine import RAGEngine

from clustering.hdbscan_cluster import HDBSCANClusterer
from clustering.subcluster import SubClusterer
from analytics.cluster_labeler import ClusterLabeler
from processing.document_purifier import DocumentPurifier
from analytics.narrative.timeline_engine import TimelineEngine
from analytics.evaluation.evaluation_engine import EvaluationEngine
from analytics.narrative.spike_detector import SpikeDetector
from analytics.narrative.evolution_engine import EvolutionEngine
from logger.evaluation_logger import EvaluationLogger
from analytics.graphs.topk_graph import TopKGraph
from analytics.graphs.graph_diagnostics import GraphDiagnostics
from analytics.graphs.community_detector import CommunityDetector
from analytics.graphs.centrality_analyzer import CentralityAnalyzer
from analytics.narrative.narrative_statistics import NarrativeStatistics
from analytics.influence_engine import InfluenceEngine
from analytics.graphs.influence_mapper import InfluenceMapper
from analytics.narrative.emerging_narrative_detector import EmergingNarrativeDetector
from analytics.narrative.forecast_engine import ForecastEngine
from analytics.narrative.early_warning_engine import EarlyWarningEngine


class AIPipeline:

    def __init__(self):

        print("Loading embedding model...")
        self.embedding_service = EmbeddingService()

        print("Initializing RAG engine...")
        self.rag = RAGEngine()

        self.vector_store = None
        self.evaluation_logger = EvaluationLogger()

    # ---------------------------------------------------
    # TEXT CHUNKING
    # ---------------------------------------------------

    def chunk_text(self, text, chunk_size=300):

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):

            chunk = " ".join(words[i:i + chunk_size])

            if len(chunk.strip()) > 50:
                chunks.append(chunk)

        return chunks

    # ---------------------------------------------------
    # BUILD VECTOR DATABASE
    # ---------------------------------------------------

    def build_vector_db(self, articles):

        print("Building vector database...")

        all_chunks = []
        purifier = DocumentPurifier()

        for article in articles:

            if not article.get("content"):
                continue
            
            #---------------------------------------------------
            # PURIFY DOCUMENT
            #---------------------------------------------------
            cleaned = purifier.clean(article["content"])

            #---------------------------------------------------
            # QUALITY CHECK
            #---------------------------------------------------
            if not purifier.is_valid(cleaned):
                continue
            
            #---------------------------------------------------
            # CHUNKING
            #---------------------------------------------------
            chunks = self.chunk_text(cleaned)
            article_date = article.get("date", "unknown")
            for chunk in chunks:

                all_chunks.append({
                    "text": chunk,
                    "date": article_date
                })

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
            min_cluster_size=12,
            min_samples=4
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
                "date": all_chunks[i]["date"]
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

            cluster_texts = [
                x["text"]
                for x in items
            ]

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

                self.subcluster_labels[
                    int(main_cluster)
                ][0] = cluster_label

                for item in items:

                    clustered_chunks.append({
                        "text": item["text"],
                        "cluster": int(main_cluster),
                        "subcluster": 0,
                        "date": item["date"]
                    })

                    filtered_embeddings.append(item["embedding"])

                continue

            # ---------------------------------------------
            # RUN SUBCLUSTERING
            # ---------------------------------------------

            sub_labels = subclusterer.cluster(
                cluster_embeddings
            )

            from collections import defaultdict

            subcluster_groups = defaultdict(list)

            for idx, sub_id in enumerate(sub_labels):

                if sub_id == -1:
                    continue

                subcluster_groups[sub_id].append(
                    items[idx]["text"]
                )

            # ---------------------------------------------
            # GENERATE SUBCLUSTER LABELS
            # ---------------------------------------------

            for sub_id, texts in subcluster_groups.items():

                try:

                    sub_label = labeler.generate_label(
                        texts[:20]
                    )

                except Exception:

                    sub_label = (
                        f"Subcluster {sub_id}"
                    )

                self.subcluster_labels[
                    int(main_cluster)
                ][int(sub_id)] = sub_label

            for idx, item in enumerate(items):

                clustered_chunks.append({
                    "text": item["text"],
                    "cluster": int(main_cluster),
                    "subcluster": int(sub_labels[idx]),
                    "date": item["date"]
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

            self.cluster_labels[
                cluster_id
            ] = rebuilt_label

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
        self.clustered_chunks = clustered_chunks

        if len(filtered_embeddings) == 0:
            raise ValueError("No clustered chunks found after noise removal.")
        
        # ---------------------------------------------------
        # VECTOR DATABASE
        # ---------------------------------------------------

        dimension = len(filtered_embeddings[0])

        self.vector_store = VectorStore(dimension)

        self.vector_store.add(
            filtered_embeddings,
            clustered_chunks
        )

        self.clustered_chunks = clustered_chunks

        print(
            "Vector DB built with",
            len(clustered_chunks),
            "clean chunks"
        )

    # ---------------------------------------------------
    # QUERY SYSTEM
    # ---------------------------------------------------

    def query(self, question):

        query_embedding = self.embedding_service.embed([question])[0]

        # ---------------------------------------------------
        # GLOBAL SEARCH
        # ---------------------------------------------------

        initial_results = self.vector_store.search(
            query_embedding,
            k=10
        )

        clusters = [r["cluster"] for r in initial_results]

        top_clusters = [
            c[0]
            for c in Counter(clusters).most_common(2)
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
                k=4
            )

            all_results.extend(cluster_results)

        # ---------------------------------------------------
        # GLOBAL RERANK
        # ---------------------------------------------------

        all_results = sorted(
            all_results,
            key=lambda x: x["score"],
            reverse=True
        )

        results = all_results[:5]
        # ---------------------------------------------
        # RETRIEVAL CONFIDENCE CHECK
        # ---------------------------------------------
        scores = [r["score"] for r in results]

        avg_score = sum(scores) / len(scores)

        if avg_score >= 0.70:

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

        if avg_score < 0.30:

            return (
                "Insufficient narrative evidence found "
                "in the current media corpus."
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

        retrieval_stats = {

            "question": question,

            "max_score": max(scores),

            "avg_score": avg_score,

            "min_score": min(scores)
        }

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
                f"📊 Confidence: "
                f"{r['score']:.4f}"
            )

            print(r["text"][:200])

            print("-" * 50)

        # ---------------------------------------------------
        # CONTEXT BUILDING
        # ---------------------------------------------------

        context = "\n\n".join([
            r["text"] 
            for r in results
        ])

        # ---------------------------------------------------
        # GENERATE RESPONSE
        # ---------------------------------------------------

        answer = self.rag.generate(
            context,
            question
        )

        return answer, retrieval_stats

    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------

    def run(self):
        logger = EvaluationLogger()

        print("Loading processed data...")

        with open(
            "data_lake/processed/enriched_articles.json",
            "r",
            encoding="utf-8"
        ) as f:

            articles = json.load(f)

        self.build_vector_db(articles)

        timeline_engine = TimelineEngine()
        timeline_engine.build(
            self.clustered_chunks,
            self.cluster_labels
        )
        timeline_engine.display()

        # ---------------------------------------------------
        # SPIKE DETECTION
        # ---------------------------------------------------

        spike_detector = SpikeDetector()

        spikes = spike_detector.detect(
            timeline_engine.timeline
        )

        spike_detector.display(spikes)

        logger.save(
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
        logger.save(
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

        logger.save(
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

        logger.save(
            "coherence_scores",
            coherence
        )

        logger.save(
            "purity_scores",
            purity
        )

        logger.save(
            "cluster_labels",
            self.cluster_labels
        )

        logger.save(
            "timeline_report",
            timeline_engine.timeline
        )

        # ---------------------------------------------------
        # NARRATIVE GRAPH
        # ---------------------------------------------------

        graph_engine = TopKGraph(k=3, min_similarity=0.30)

        graph = graph_engine.build(

            self.cluster_groups,

            self.cluster_labels
        )

        graph_engine.display_summary()

        community_detector = CommunityDetector()

        communities = community_detector.detect(
            graph
        )

        community_detector.display(
            communities,
            graph
        )


        centrality = CentralityAnalyzer()

        centrality_results = centrality.analyze(
            graph
        )

        centrality.display(
            graph,
            centrality_results
        )

        stats_engine = NarrativeStatistics()

        narrative_stats = stats_engine.generate(
            self.clustered_chunks,
            self.cluster_labels
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

        influence_engine.display(
            influence_scores
        )


        mapper = InfluenceMapper()

        mappings = mapper.generate(
            graph,
            influence_scores
        )

        mapper.display(
            mappings
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

        logger.save(
            "forecast_report",
            forecasts
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

        logger.save(
            "early_warning_report",
            warnings
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
        logger.save(
            "graph_diagnostics",
            diagnostics
        )



        print("Ready for queries!\n")

        while True:

            q = input("Ask a question (or 'exit'): ")

            if q.lower() == "exit":
                break

            response, retrieval_stats = self.query(q)
            


            print("\n🧠 Intelligence Report:\n")

            print(response)

            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":

    pipeline = AIPipeline()

    pipeline.run()
