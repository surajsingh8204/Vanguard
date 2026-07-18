import math

from datetime import datetime, timezone

from backend.src.services.artifact_service import artifact_service


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


class ReportService:

    def _report_metadata(self, report_path):
        latest_run = datetime.fromtimestamp(
            report_path.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()
        return {
            "report_type": report_path.stem.rsplit("_", 1)[0],
            "created_at": latest_run,
            "latest_run": latest_run,
            "filename": report_path.name,
            "status": "available",
        }

    def latest(self, page=1, limit=25, report_type=None):
        reports = artifact_service.list_reports()

        if report_type:
            reports = [
                report for report in reports
                if report.stem.startswith(f"{report_type}_")
            ]

        page = max(int(page), 1)
        limit = max(int(limit), 1)
        start = (page - 1) * limit
        end = start + limit

        items = [self._report_metadata(report) for report in reports[start:end]]

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": len(reports),
            "pages": (len(reports) + limit - 1) // limit if reports else 0,
        }

    def history(self, page=1, limit=100, report_type=None):
        return self.latest(page=page, limit=limit, report_type=report_type)

    def content(self, filename):
        # Only allow files that actually exist inside evaluation_logs
        # to prevent path traversal.
        known = {report.name: report for report in artifact_service.list_reports()}
        report_path = known.get(filename)
        if report_path is None:
            raise ValueError(f"Report not found: {filename}")

        data = artifact_service.load_report_json(filename)
        return {
            **self._report_metadata(report_path),
            "content": _json_safe(data),
        }


report_service = ReportService()