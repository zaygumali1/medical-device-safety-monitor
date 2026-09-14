from pathlib import Path
import pandas as pd
import json
from src.logger import get_logger

logger=get_logger(__name__)


EVENT_COLUMNS = [
    "report_number",
    "event_type",
    "event_location",
    "date_of_event",
    "date_received",
    "date_report",
    "report_source_code",
    "adverse_event_flag",
    "health_professional",
    "number_devices_in_event",
    "number_patients_in_event",
    "manufacturer_name"
]

DEVICE_COLUMNS =[
"report_number",
"device_event_key",
"device_sequence_number",
"brand_name",
"generic_name",
"manufacturer_d_name",
"model_number",
"catalog_number",
"lot_number",
"device_operator",
"device_availability",
"device_report_product_code",
"device_age_text",
"device_evaluated_by_manufacturer",
"implant_flag",
]

PATIENT_COLUMNS = [
    "report_number",
    "patient_sequence_number",
    "date_received",
    "patient_age",
    "patient_sex",
    "patient_weight",
    "patient_ethnicity",
    "patient_race",
]

MDR_TEXT_COLUMNS = [
    "report_number",
    "mdr_text_key",
    "text_type_code",
    "patient_sequence_number",
    "text",
]


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
    return device_normalized_df.reindex(columns=DEVICE_COLUMNS)


def transform_patients(raw_response:list[dict]) -> pd.DataFrame:
    records=prepare_records(raw_response,"patient")
    patient_normalized_df=pd.json_normalize(records,record_path="patient",meta=["report_number"])
    if patient_normalized_df.empty:
        return pd.DataFrame(columns=PATIENT_COLUMNS)
    return patient_normalized_df.reindex(columns=PATIENT_COLUMNS)


def transform_mdr_text(raw_response:list[dict]) -> pd.DataFrame:
    records=prepare_records(raw_response,"mdr_text")
    mdr_normalized_df=pd.json_normalize(records,record_path="mdr_text",meta=["report_number"])
    if mdr_normalized_df.empty:
        return pd.DataFrame(columns=MDR_TEXT_COLUMNS)
    return mdr_normalized_df.reindex(columns=MDR_TEXT_COLUMNS)


def validate_required_fields(df: pd.DataFrame,required_columns: list[str]) -> pd.DataFrame:
    invalid_rows=[]
    for index,row in df.iterrows():
        missing_cols=[]
        for col in required_columns:
            if pd.isna(row[col]):
                missing_cols.append(col)

        if missing_cols:
            invalid_rows.append({"report_number":row["report_number"],"missing_cols":missing_cols})
    return pd.DataFrame(invalid_rows)