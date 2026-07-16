from datetime import datetime


class TimeUtils:

    @staticmethod
    def format_gdelt_time(raw_time):

        try:
            dt = datetime.strptime(raw_time, "%Y%m%d%H%M%S")
            return dt.isoformat()
        except:
            return None