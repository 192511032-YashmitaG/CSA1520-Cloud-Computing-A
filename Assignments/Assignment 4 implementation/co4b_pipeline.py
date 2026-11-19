"""
CO4 Assignment 4 Part II - reproducible Big Data engineering lab.
All datasets are synthetic. Run: python run_all.py
Python 3.10+, pandas, numpy, matplotlib, cryptography, python-docx.
"""
from pathlib import Path
import json, hashlib, sqlite3, time, csv, statistics
import numpy as np
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def map_shuffle_reduce(df, reducers=8):
    valid=df.dropna(subset=["speed_kmh"]).query("0 <= speed_kmh <= 200").copy()
    valid["hour"]=valid["event_time"].dt.floor("h")
    valid["partition"]=valid["segment"] % reducers
    mapped=valid.groupby(["partition","segment","hour"])["speed_kmh"].agg(["sum","count"]).reset_index()
    reduced=mapped.groupby(["segment","hour"]).agg(total=("sum","sum"),count=("count","sum")).reset_index()
    reduced["average_speed"]=reduced.total/reduced["count"]
    return reduced, {"read":len(df),"accepted":len(valid),"rejected":len(df)-len(valid),
                     "reducer_load":valid.groupby("partition").size().to_dict(),"shuffle_groups":len(mapped)}

def batch_one_minute(events):
    groups={}
    for e in events:
        h,m,s=map(int,e["event"].split(":")); groups.setdefault((e["segment"],h,m),[]).append(e["speed"])
    return {str(k):sum(v)/len(v) for k,v in groups.items()}

def stream_one_minute(events, watermark_seconds=15, deduplicate=True):
    seen=set(); maximum=-1; state={}; dropped=[]
    for e in sorted(events,key=lambda x:x["arrival"]):
        identity=(e["id"],e["event"])
        if deduplicate and identity in seen: dropped.append((e["id"],"duplicate")); continue
        seen.add(identity)
        h,m,s=map(int,e["event"].split(":")); event_second=h*3600+m*60+s
        if maximum>=0 and event_second < maximum-watermark_seconds:
            dropped.append((e["id"],"late")); continue
        maximum=max(maximum,event_second)
        state.setdefault((e["segment"],h,m),[]).append(e["speed"])
    return {str(k):sum(v)/len(v) for k,v in state.items()},dropped

def clean_records(rows):
    required={"event_id","sensor","segment","speed_kmh","event_time"}; seen=set(); good=[]; quarantine=[]
    for line,row in enumerate(rows,1):
        reason=None
        if not required.issubset(row): reason="SCHEMA_MISSING_FIELD"
        elif row["event_id"] in seen: reason="DUPLICATE_EVENT_ID"
        elif row["speed_kmh"] is None: reason="MISSING_SPEED"
        elif not isinstance(row["speed_kmh"],(int,float)) or not 0<=row["speed_kmh"]<=200: reason="INVALID_SPEED"
        else:
            try: pd.to_datetime(row["event_time"],utc=True,errors="raise")
            except Exception: reason="MALFORMED_EVENT_TIME"
        if reason: quarantine.append({"line":line,"reason":reason,"record":row})
        else: seen.add(row["event_id"]); good.append(row)
    return good,quarantine

def fraud_keyed(events):
    state={}
    for e in events: state.setdefault(e["account"],[]).append(e)
    flags={}
    for account,rows in state.items():
        for current in rows:
            window=[r for r in rows if current["day"]-6<=r["day"]<=current["day"]]
            beneficiaries=sorted({r["beneficiary"] for r in window})
            if len(beneficiaries)>=3: flags[account]={"beneficiaries":beneficiaries,"days":sorted({r["day"] for r in window})}
    return flags

def fraud_naive(events):
    comparisons=0
    for a in events:
        for b in events:
            comparisons+=1
            _=a["account"]==b["account"]
    return fraud_keyed(events),comparisons

if __name__=="__main__":
    print("Import the functions above or execute the bundled evidence generator.")


def privacy_linkage_and_k_anonymity(beneficiaries, auxiliary):
    released=beneficiaries.drop(columns=["Name","ID_Number"])
    matches=auxiliary.merge(released,on=["PIN_Code","Date_of_Birth","Gender"],how="inner")
    generalized=released.copy()
    ages=(pd.Timestamp("2026-01-01")-pd.to_datetime(generalized["Date_of_Birth"])).dt.days//365
    generalized["PIN_region"]=generalized["PIN_Code"].str[:1]
    generalized["Age_band"]=(ages//10*10).astype(str)+"s"
    generalized=generalized.drop(columns=["PIN_Code","Date_of_Birth"])
    sizes=generalized.groupby(["PIN_region","Age_band","Gender"]).size()
    return matches, int(sizes.min()), generalized

def detect_tampering(frame):
    original=hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest()
    altered=frame.copy(); altered.loc[0,altered.columns[-1]] = altered.iloc[0,-1] + 1
    changed=hashlib.sha256(altered.to_csv(index=False).encode()).hexdigest()
    return original, changed, original != changed

def storage_query_sqlite(database, sensor_id, day):
    con=sqlite3.connect(database)
    try:
        return con.execute("SELECT * FROM traffic WHERE sensor_id=? AND day=?",(sensor_id,day)).fetchall()
    finally:
        con.close()

def fraud_keyed_sliding_window(events):
    by_account={}
    for event in events:
        by_account.setdefault(event["account"],[]).append(event)
    flags={}
    for account,rows in by_account.items():
        for current in rows:
            active=[r for r in rows if current["day"]-6 <= r["day"] <= current["day"]]
            beneficiaries=sorted({r["beneficiary"] for r in active})
            if len(beneficiaries)>=3:
                flags[account]={"beneficiaries":beneficiaries,"days":sorted({r["day"] for r in active})}
    return flags
