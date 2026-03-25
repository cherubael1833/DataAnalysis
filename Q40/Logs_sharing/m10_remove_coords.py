import serial
import pyubx2
import json
from pathlib import Path
from datetime import datetime, timezone

binary_log = Path("raw_log.jsonl")
decoded_log = Path("decoded_log.jsonl")

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("++00:00","Z")

def append_jsonl(path: Path, record: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, separators=(",", ":"), default=str))
        f.write("\n")

NAV_PVT_FIELDS = [
    "iTOW","year", "month", "day","hour", "min", "second",
    "validDate", "validTime", "fullyResolved", "validMag",
    "tAcc", "nano","fixType", "gnssFixOk", "diffSoln",
    "psmState", "headVehValid", "carrSoln", "confirmedAvai", 
    "confirmedDate", "confirmedTime","numSV","lon", "lat",
    "height", "hMSL","hAcc", "vAcc","velN", "velE", "velD",
    "gSpeed", "headMot","sAcc", "headAcc", "pDOP","invalidLlh",
    "lastCorrectionAge","authTime","nmaFixStatus","reserved0",
    "headVeh","magDec", "magAcc"]

def nav_pvt_to_dict(parsed_data, ts):
    decoded = {"ts": ts}
    decoded.update({field: getattr(parsed_data, field, None)
        for field in NAV_PVT_FIELDS
    })
    return decoded

while True:
    with serial.Serial(port="/dev/cu.usbserial-0001",baudrate=115200,timeout=0.1) as stream:
        ubr=pyubx2.UBXReader(stream,protfilter=2)
        raw_data, parsed_data = ubr.read()
        
        if parsed_data is not None:
            ts = utc_now_iso()
            append_jsonl(binary_log, {"ts": ts,"UBX": raw_data.hex()})
            decoded = nav_pvt_to_dict(parsed_data, ts)
            append_jsonl(decoded_log, decoded)
            




            
    