from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from datetime import datetime, timedelta

from app.sftp_client import SFTPClient
from app.csv_service import parse_csv, is_valid_row
from app.config import settings

app = FastAPI(title="Semantan Data Logger API")

# Ganti allow_origins nanti dengan domain vercel kamu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sftp_client = SFTPClient()


# ==============================
# ENDPOINT: GET LATEST
# ==============================


@app.get("/latest")
def get_latest():

    files = sftp_client.list_files()
    csv_files = [f for f in files if f.filename.endswith(".csv")]

    if not csv_files:
        raise HTTPException(status_code=404, detail="No CSV files found")

    latest_file = max(csv_files, key=lambda x: x.st_mtime)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        sftp_client.download_file(latest_file.filename, tmp.name)
        data = parse_csv(tmp.name)

    if not data:
        raise HTTPException(status_code=404, detail="No valid data")

    # Scan dari belakang cari row valid
    for row in reversed(data):
        if is_valid_row(row):
            return {"file": latest_file.filename, "latest": row}

    raise HTTPException(status_code=404, detail="No non-empty valid data found")


# ==============================
# ENDPOINT: DATE RANGE
# ==============================


@app.get("/by-date-range")
def get_by_date_range(
    start: str = Query(..., example="2026-02-23"),
    end: str = Query(..., example="2026-02-24"),
):

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date"
        )

    # Optional safety limit (misal max 14 hari)
    if (end_date - start_date).days > 14:
        raise HTTPException(status_code=400, detail="Maximum range is 14 days")

    all_data = []
    files_used = []

    current_date = start_date
    while current_date <= end_date:

        formatted = current_date.strftime("%Y%m%d")
        filename = f"SemantanDataLogger_{formatted}.csv"

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                sftp_client.download_file(filename, tmp.name)
            except:
                current_date += timedelta(days=1)
                continue

            parsed = parse_csv(tmp.name)
            all_data.extend(parsed)
            files_used.append(filename)

        current_date += timedelta(days=1)

    if not all_data:
        raise HTTPException(status_code=404, detail="No data found in range")

    return {
        "start": start,
        "end": end,
        "files_used": files_used,
        "total_rows": len(all_data),
        "data": all_data,
    }
