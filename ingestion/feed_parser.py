import csv
import logging
import sys
import zipfile


logger = logging.getLogger(__name__)


def _configure_csv_field_limit():

    limit = sys.maxsize

    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit = limit // 10


def parse_gkg(path):

    articles = []
    _configure_csv_field_limit()

    try:
        with zipfile.ZipFile(path, "r") as archive:

            file_name = archive.namelist()[0]

            with archive.open(file_name) as handle:

                reader = csv.reader(
                    (
                        line.decode("utf-8", errors="ignore")
                        for line in handle
                    ),
                    delimiter="\t",
                )

                for row in reader:

                    try:
                        url = row[4]
                    except IndexError:
                        continue

                    if not url.startswith("http"):
                        continue

                    articles.append(
                        {
                            "date": row[1] if len(row) > 1 else None,
                            "source": row[3] if len(row) > 3 else None,
                            "url": url,
                        }
                    )

    except (FileNotFoundError, zipfile.BadZipFile, OSError, csv.Error) as exc:
        logger.exception("Error parsing feed %s: %s", path, exc)

    return articles
