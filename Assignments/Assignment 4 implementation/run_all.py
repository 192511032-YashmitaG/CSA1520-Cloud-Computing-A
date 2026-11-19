from pathlib import Path
import json
import pandas as pd
from src.co4b_pipeline import map_shuffle_reduce, clean_records, fraud_keyed_sliding_window

ROOT=Path(__file__).resolve().parent
traffic=pd.read_csv(ROOT/"data"/"traffic_batch_600k.csv",parse_dates=["event_time"])
hourly,metrics=map_shuffle_reduce(traffic)
hourly.to_csv(ROOT/"results"/"rerun_task1_hourly.csv",index=False)
print("Task 1 rerun:",metrics)

raw=json.loads((ROOT/"data"/"task4_raw_events.json").read_text())
cleaned,quarantine=clean_records(raw)
print("Task 4 rerun: kept",len(cleaned),"quarantined",len(quarantine))

print("The complete Task 2, Task 3, Task 5 and Task 6 reference inputs, generated outputs and evidence are included in data/, results/ and evidence/.")
print("Task-specific reusable functions are in src/co4b_pipeline.py.")
