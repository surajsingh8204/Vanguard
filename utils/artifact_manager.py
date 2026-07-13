import os
import json

try:
    import numpy as np
except ImportError:
    np = None


class ArtifactManager:

    def _make_json_key(self, key):

        key = self._make_json_safe(key)

        if isinstance(key, (str, int, float, bool)) or key is None:
            return key

        return str(key)

    def _make_json_safe(self, value):

        if isinstance(value, dict):
            return {
                self._make_json_key(key): self._make_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self._make_json_safe(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                self._make_json_safe(item)
                for item in value
            ]

        if np is not None and isinstance(value, np.ndarray):
            return self._make_json_safe(
                value.tolist()
            )

        if np is not None and isinstance(value, np.integer):
            return int(value)

        if np is not None and isinstance(value, np.floating):
            return float(value)

        if np is not None and isinstance(value, np.bool_):
            return bool(value)

        return value

    # -----------------------------------------
    # SAVE JSON
    # -----------------------------------------

    def save_json(

        self,

        path,

        data

    ):

        os.makedirs(

            os.path.dirname(path),

            exist_ok=True

        )

        safe_data = self._make_json_safe(data)

        with open(

            path,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                safe_data,

                f,

                indent=4,

                ensure_ascii=False

            )

    # -----------------------------------------
    # LOAD JSON
    # -----------------------------------------

    def load_json(

        self,

        path

    ):

        if not os.path.exists(path):

            return None

        try:

            with open(

                path,

                "r",

                encoding="utf-8"

            ) as f:

                return json.load(f)

        except json.JSONDecodeError:

            return None

    # -----------------------------------------
    # EXISTS
    # -----------------------------------------

    def exists(

        self,

        path

    ):

        if not os.path.exists(path):

            return False

        if path.endswith(".json"):

            return self.load_json(path) is not None

        return True

    def analytics_exist(self):

        files = [
            "artifacts/analytics/timeline.json",
            "artifacts/analytics/forecasts.json",
            "artifacts/analytics/early_warnings.json",
            "artifacts/analytics/influence_scores.json",
            "artifacts/analytics/executive_brief.json"
        ]

        return all(
            os.path.exists(f)
            for f in files
        )
