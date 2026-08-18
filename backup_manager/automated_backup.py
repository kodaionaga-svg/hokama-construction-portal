"""施工管理データをSupabaseから取得し、ZIPとして保存する定期バックアップ用スクリプト。"""

from __future__ import annotations

import csv
import io
import json
import os
import urllib.parse
import urllib.error
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


def rest_request(base_url: str, service_key: str, table: str, *, method: str = "GET", body: dict | None = None) -> list[dict]:
    url = f"{base_url.rstrip('/')}/rest/v1/{urllib.parse.quote(table)}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload) if payload else []


def backup_is_due(base_url: str, service_key: str) -> bool:
    if os.environ.get("FORCE_BACKUP", "").lower() == "true":
        return True
    url = f"{base_url.rstrip('/')}/rest/v1/automated_backup_runs?select=created_at&order=created_at.desc&limit=1"
    request = urllib.request.Request(url, headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        rows = json.loads(response.read().decode("utf-8"))
    if not rows:
        return True
    previous = datetime.fromisoformat(rows[0]["created_at"].replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - previous).total_seconds() >= 72 * 60 * 60


def storage_request(
    base_url: str,
    service_key: str,
    path: str,
    *,
    data: bytes | None = None,
    method: str | None = None,
    content_type: str = "application/json",
    extra_headers: dict[str, str] | None = None,
) -> bytes:
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": content_type,
    }
    headers.update(extra_headers or {})
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/storage/v1/{path.lstrip('/')}",
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Storage API error {exc.code}: {detail}") from exc


def list_storage_files(base_url: str, service_key: str, bucket: str, prefix: str = "") -> list[str]:
    payload = json.dumps({"prefix": prefix, "limit": 1000, "offset": 0}).encode("utf-8")
    items = json.loads(storage_request(base_url, service_key, f"object/list/{bucket}", data=payload))
    files: list[str] = []
    for item in items:
        name = item.get("name", "")
        if not name:
            continue
        full_name = f"{prefix}/{name}".strip("/")
        if item.get("id"):
            files.append(full_name)
        else:
            files.extend(list_storage_files(base_url, service_key, bucket, full_name))
    return files


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
    if not backup_is_due(base_url, service_key):
        print("前回の成功バックアップから72時間未満のため、今回は実行しません。")
        return
    out_dir = Path(os.environ.get("BACKUP_OUTPUT_DIR", "backup-output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = out_dir / f"hokama-construction-backup-{stamp}.zip"
    results: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}
    storage_files: list[tuple[str, bytes]] = []
    for table in TABLES:
        try:
            results[table] = fetch_table(base_url, service_key, table)
        except Exception as exc:  # Keep a usable backup when a legacy table is absent.
            errors[table] = str(exc)

    try:
        buckets = json.loads(storage_request(base_url, service_key, "bucket"))
        for bucket in buckets:
            bucket_name = bucket["name"]
            if bucket_name == "construction-backups":
                continue
            for file_name in list_storage_files(base_url, service_key, bucket_name):
                encoded = "/".join(urllib.parse.quote(part) for part in file_name.split("/"))
                storage_files.append((f"storage/{bucket_name}/{file_name}", storage_request(base_url, service_key, f"object/{bucket_name}/{encoded}")))
    except Exception as exc:
        errors["storage"] = str(exc)

    manifest = {
        "created_at": created,
        "format": "hokama-construction-backup/v1",
        "tables": {table: len(rows) for table, rows in results.items()},
        "errors": errors,
        "storage_files": len(storage_files),
    }
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr("README.txt", "株式会社ホカマ 建築部施工管理ポータル：自動バックアップ\n")
        for table, rows in results.items():
            archive.writestr(f"data/{table}.csv", csv_bytes(rows))
        for backup_path, contents in storage_files:
            archive.writestr(backup_path, contents)
    uploaded_name = f"automatic/{output_path.name}"
    storage_request(
        base_url,
        service_key,
        f"object/construction-backups/{urllib.parse.quote(uploaded_name, safe='/')}",
        data=output_path.read_bytes(),
        method="POST",
        content_type="application/zip",
        extra_headers={"x-upsert": "true"},
    )
    rest_request(
        base_url,
        service_key,
        "automated_backup_runs",
        method="POST",
        body={
            "file_name": uploaded_name,
            "table_count": len(results),
            "storage_file_count": len(storage_files),
        },
    )
    print(json.dumps({"file": str(output_path), "tables": manifest["tables"], "errors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()

