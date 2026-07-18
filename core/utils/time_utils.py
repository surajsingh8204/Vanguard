from datetime import datetime


class TimeUtils:

    @staticmethod
    def format_gdelt_time(raw_time):

        try:
            dt = datetime.strptime(raw_time, "%Y%m%d%H%M%S")
            return dt.isoformat()
        except:
            return None

    @staticmethod
    def parse_to_day(raw_date):
        """Parse a chunk/article date in any supported format to 'YYYY-MM-DD'.

        Supports ISO timestamps, plain dates, and GDELT compact formats.
        Returns None when the value cannot be parsed (e.g. 'Unknown Date').
        """

        if not raw_date or not isinstance(raw_date, str):
            return None

        value = raw_date.strip()

        if not value:
            return None

        formats = (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M",
            "%Y%m%d",
        )

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

        return None