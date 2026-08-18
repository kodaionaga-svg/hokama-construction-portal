"""施工管理データをSupabaseから取得し、ZIPとして保存する定期バックアップ用スクリプト。"""

from __future__ import annotations

import csv
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


TABLES = [
    "daily_report_projects", "daily_reports",
    "survey_projects", "survey_points", "survey_observations",
    "issue_projects", "issues",
    "site_announcements", "notice_projects",
    "schedule_projects", "project_schedule_pdfs",
    "patrol_sites", "patrol_check_items", "patrol_checks", "patrol_findings", "patrol_report_settings",
    "architectural_projects", "architectural_issues", "architectural_photos",
]


def fetch_table(base_url: str, service_key: str, table: str) -> list[dict]:
    url = f"{base_url.rstrip('/')}/rest/v1/{urllib.parse.quote(table)}?select=*"
    request = urllib.request.Request(
        url,
        headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def csv_bytes(rows: list[dict]) -> bytes:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def main() -> None:
    base_url = os.environ["SUPABASE_URL"]
    service_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    out_dir = Path(os.environ.get("BACKUP_OUTPUT_DIR", "backup-output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = out_dir / f"hokama-construction-backup-{stamp}.zip"
    results: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}
    for table in TABLES:
        try:
            results[table] = fetch_table(base_url, service_key, table)
        except Exception as exc:  # Keep a usable backup when a legacy table is absent.
            errors[table] = str(exc)

    manifest = {
        "created_at": created,
        "format": "hokama-construction-backup/v1",
        "tables": {table: len(rows) for table, rows in results.items()},
        "errors": errors,
        "note": "CSV files contain database records. Storage files are backed up separately in the next version.",
    }
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr("README.txt", "株式会社ホカマ 建築部施工管理ポータル：自動バックアップ\n")
        for table, rows in results.items():
            archive.writestr(f"data/{table}.csv", csv_bytes(rows))
    print(json.dumps({"file": str(output_path), "tables": manifest["tables"], "errors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()

