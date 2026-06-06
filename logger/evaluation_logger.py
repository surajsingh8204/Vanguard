import json
import os
from datetime import datetime

try:
    import numpy as np
except ImportError:
    np = None


class EvaluationLogger:

    def __init__(self):

        self.log_dir = "evaluation_logs"

        os.makedirs(
            self.log_dir,
            exist_ok=True
        )

    # ---------------------------------------------------
    # SAVE JSON REPORT
    # ---------------------------------------------------

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

    def save(

        self,

        name,

        data
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"{name}_{timestamp}.json"
        )

        path = os.path.join(
            self.log_dir,
            filename
        )

        with open(path, "w") as f:

            json.dump(
                self._make_json_safe(data),
                f,
                indent=4
            )

        print(
            f"\n💾 Saved evaluation log: {path}"
        )
