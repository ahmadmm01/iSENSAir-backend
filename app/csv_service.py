import csv
from datetime import datetime

EXPECTED_COLUMNS = 21


def safe_float(value):
    try:
        return float(value)
    except:
        return None


def safe_int(value):
    try:
        return int(value)
    except:
        return None


def parse_timestamp(value: str):
    try:
        return datetime.strptime(value.strip('"'), "%d/%m/%Y, %H:%M:%S").isoformat()
    except:
        return None


def is_valid_row(row: dict) -> bool:

    if not row.get("timestamp"):
        return False

    sensors = ["DO_Sensor", "pH_Sensor", "COD_Sensor", "BOD_Sensor", "Tr_Sensor"]

    for sensor in sensors:
        value = row.get(sensor)
        if value is not None and abs(value) > 1e-6:
            return True

    return False


def parse_csv(filepath: str):
    data = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        if not header:
            return data

        for row in reader:

            if len(row) != EXPECTED_COLUMNS:
                continue

            timestamp = parse_timestamp(row[0])
            if not timestamp:
                continue

            parsed = {
                "timestamp": timestamp,
                "device_id": row[1],
                "Tr_Sensor": safe_float(row[2]),
                "BOD_Sensor": safe_float(row[3]),
                "DO_Sensor": safe_float(row[4]),
                "COD_Sensor": safe_float(row[5]),
                "NH_Sensor": safe_float(row[6]),
                "TDS_Sensor": safe_float(row[7]),
                "CT_Sensor": safe_float(row[8]),
                "ORP_Sensor": safe_float(row[9]),
                "pH_Sensor": safe_float(row[10]),
                "Battery_Voltage": safe_float(row[11]),
                "Battery_SOC": safe_int(row[12]),
                "Charging_Current": safe_float(row[13]),
                "Charging_Power": safe_float(row[14]),
                "Pv_Power": safe_float(row[15]),
                "ChargeSet_SOC": safe_int(row[16]),
                "Fault_Code": safe_int(row[17]),
                "Inverter_State": safe_int(row[18]),
                "Valve_State": safe_int(row[19]),
                "Pump_State": safe_int(row[20]),
            }

            data.append(parsed)

    return data
