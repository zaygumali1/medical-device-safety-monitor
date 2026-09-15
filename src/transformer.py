from pathlib import Path
import pandas as pd
import json
from src.logger import get_logger
from src.config import load_yaml_config

logger=get_logger(__name__)


SCHEMAS=load_yaml_config("configs/settings.yaml").get("schemas",{})
EVENT_COLUMNS=SCHEMAS.get("events",{}).get("columns")
DEVICE_COLUMNS=SCHEMAS.get("devices",{}).get("columns")
PATIENT_COLUMNS=SCHEMAS.get("patients",{}).get("columns")
MDR_TEXT_COLUMNS=SCHEMAS.get("mdr_text",{}).get("columns")

REQUIRED_EVENT_COLUMNS=SCHEMAS.get("events",{}).get("required")
REQUIRED_DEVICE_COLUMNS=SCHEMAS.get("devices",{}).get("required")
REQUIRED_PATIENT_COLUMNS=SCHEMAS.get("patients",{}).get("required")
REQUIRED_MDR_TEXT_COLUMNS=SCHEMAS.get("mdr_text",{}).get("required")





def load_raw_response(filepath: Path) -> dict:
    with open(file=filepath,mode='r',encoding='utf-8') as file:
        api_data=json.load(file)
        return api_data         #api_data['results']


def prepare_records(raw_response: list[dict],nested_field: str) -> list[dict]:
    records=[]
    for record in raw_response:
        record=record.copy()
        if not isinstance(record.get(nested_field), list):
            logger.warning(f"Missing or invalid type found for '{nested_field} in report {record.get('report_number')}")
            record[nested_field]=[]
        records.append(record)
    return records
    

def transform_events(raw_response:list[dict])-> pd.DataFrame:
    event_df=pd.DataFrame(raw_response)
    return event_df.reindex(columns=EVENT_COLUMNS)

def transform_devices(raw_response: list[dict]) -> pd.DataFrame:
    records=prepare_records(raw_response,"device")
    device_normalized_df=pd.json_normalize(records,record_path="device",meta=["report_number"])
    if device_normalized_df.empty:
        return pd.DataFrame(columns=DEVICE_COLUMNS)
    validate_schema(device_normalized_df,REQUIRED_DEVICE_COLUMNS)
    return device_normalized_df.reindex(columns=DEVICE_COLUMNS)


def transform_patients(raw_response:list[dict]) -> pd.DataFrame:
    records=prepare_records(raw_response,"patient")
    patient_normalized_df=pd.json_normalize(records,record_path="patient",meta=["report_number"])
    if patient_normalized_df.empty:
        return pd.DataFrame(columns=PATIENT_COLUMNS)
    validate_schema(patient_normalized_df,REQUIRED_PATIENT_COLUMNS)
    return patient_normalized_df.reindex(columns=PATIENT_COLUMNS)


def transform_mdr_text(raw_response:list[dict]) -> pd.DataFrame:
    records=prepare_records(raw_response,"mdr_text")
    mdr_normalized_df=pd.json_normalize(records,record_path="mdr_text",meta=["report_number"])
    if mdr_normalized_df.empty:
        return pd.DataFrame(columns=MDR_TEXT_COLUMNS)
    validate_schema(mdr_normalized_df,REQUIRED_MDR_TEXT_COLUMNS)
    return mdr_normalized_df.reindex(columns=MDR_TEXT_COLUMNS)




def validate_schema(df : pd.DataFrame, expected_columns : list[str]):
    actual_cols=set(df.columns)
    expected_cols=set(expected_columns)
    if (expected_cols-actual_cols):
        raise ValueError(f"schema validation error, missing columns {expected_cols-actual_cols}")




def validate_required_fields(df: pd.DataFrame,required_columns: list[str]) -> pd.DataFrame:
    invalid_rows=[]
    for index,row in df.iterrows():
        missing_cols=[]
        for col in required_columns:
            if pd.isna(row[col])  or (isinstance(row[col],str) and row[col].strip()==""):
                missing_cols.append(col)

        if missing_cols:
            invalid_rows.append({"report_number":row["report_number"],"missing_cols":missing_cols})
    return pd.DataFrame(invalid_rows)