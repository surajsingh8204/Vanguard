from datetime import datetime, timedelta


class TimeUtils:

    _DATETIME_FORMATS = (
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:00",
        "%Y-%m-%d",
        "%Y%m%d%H%M%S",
        "%Y%m%d%H%M",
        "%Y%m%d",
    )

    @staticmethod
    def format_gdelt_time(raw_time):
        try:
            dt = datetime.strptime(raw_time, "%Y%m%d%H%M%S")
            return dt.isoformat()
        except Exception:
            return None

    @staticmethod
    def parse_datetime(raw_date):
        """Parse a date string into a datetime, or None if unsupported."""

        if not raw_date or not isinstance(raw_date, str):
            return None

        value = raw_date.strip()
        if not value:
            return None

        for fmt in TimeUtils._DATETIME_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def parse_to_day(raw_date):
        """Parse a chunk/article date to 'YYYY-MM-DD'."""

        dt = TimeUtils.parse_datetime(raw_date)
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def parse_to_hour(raw_date):
        """Parse a chunk/article date to 'YYYY-MM-DDTHH:00'."""

        dt = TimeUtils.parse_datetime(raw_date)
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%dT%H:00")

    @staticmethod
    def fill_contiguous_buckets(counts):
        """Fill missing day/hour buckets with zeros between first and last."""

        if not counts:
            return {}

        keys = sorted(counts.keys())
        first = keys[0]
        last = keys[-1]

        if "T" in first:
            fmt = "%Y-%m-%dT%H:00"
            step = timedelta(hours=1)
        else:
            fmt = "%Y-%m-%d"
            step = timedelta(days=1)

        start = datetime.strptime(first, fmt)
        end = datetime.strptime(last, fmt)
        filled = {}
        cursor = start
        while cursor <= end:
            key = cursor.strftime(fmt)
            filled[key] = int(counts.get(key, 0))
            cursor += step
        return filled
