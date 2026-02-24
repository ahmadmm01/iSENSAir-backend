from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from datetime import datetime, timedelta

from app.sftp_client import SFTPClient
from app.csv_service import parse_csv, is_valid_row
from app.config import settings

app = FastAPI(title="iSENSAir Data Logger API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sftp_client = SFTPClient()


def validate_location(location: str):
    if location not in settings.LOCATIONS:
        raise HTTPException(status_code=400, detail="Invalid location")


# ===============================
# STATUS
# ===============================
@app.get("/")
def get_status():
    return {"status": "ok", "locations": list(settings.LOCATIONS.keys())}


# ===============================
# LATEST
# ===============================


@app.get("/latest")
def get_latest(location: str = Query(..., example="semantan")):

    validate_location(location)

    files = sftp_client.list_files(location)
    csv_files = [f for f in files if f.filename.endswith(".csv")]

    if not csv_files:
        raise HTTPException(status_code=404, detail="No CSV files found")

    # Urutkan dari terbaru ke terlama
    sorted_files = sorted(csv_files, key=lambda x: x.st_mtime, reverse=True)

    for file_attr in sorted_files:

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                sftp_client.download_file(location, file_attr.filename, tmp.name)
            except:
                continue

            data = parse_csv(tmp.name)

        # Cari row valid terakhir di file ini
        for row in reversed(data):
            if is_valid_row(row):
                return {"location": location, "file": file_attr.filename, "latest": row}

    # Kalau semua file kosong
    raise HTTPException(status_code=404, detail="No valid data found in any file")


# ===============================
# BY DATE RANGE
# ===============================


@app.get("/by-date-range")
def get_by_date_range(
    location: str = Query(..., example="semantan"),
    start: str = Query(..., example="2026-02-23"),
    end: str = Query(..., example="2026-02-24"),
):

    validate_location(location)

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date"
        )

    if (end_date - start_date).days > 14:
        raise HTTPException(status_code=400, detail="Maximum range is 14 days")

    prefix = settings.LOCATIONS[location]["prefix"]

    all_data = []
    files_used = []

    current_date = start_date

    while current_date <= end_date:

        formatted = current_date.strftime("%Y%m%d")
        filename = f"{prefix}{formatted}.csv"

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                sftp_client.download_file(location, filename, tmp.name)
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
        "location": location,
        "start": start,
        "end": end,
        "files_used": files_used,
        "total_rows": len(all_data),
        "data": all_data,
    }
