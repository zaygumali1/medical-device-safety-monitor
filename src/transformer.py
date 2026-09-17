from pathlib import Path
import pandas as pd
import json
from src.logger import get_logger
from src.config import load_yaml_config

logger=get_logger(__name__)


# # SCHEMAS=load_yaml_config("configs/settings.yaml").get("schemas",{})
# EVENT_COLUMNS=SCHEMAS.get("events",{}).get("columns")
# DEVICE_COLUMNS=SCHEMAS.get("devices",{}).get("columns")
# PATIENT_COLUMNS=SCHEMAS.get("patients",{}).get("columns")
# MDR_TEXT_COLUMNS=SCHEMAS.get("mdr_text",{}).get("columns")

# REQUIRED_EVENT_COLUMNS=SCHEMAS.get("events",{}).get("required")
# REQUIRED_DEVICE_COLUMNS=SCHEMAS.get("devices",{}).get("required")
# REQUIRED_PATIENT_COLUMNS=SCHEMAS.get("patients",{}).get("required")
# REQUIRED_MDR_TEXT_COLUMNS=SCHEMAS.get("mdr_text",{}).get("required")





def load_raw_response(filepath: Path) -> dict:
    with open(file=filepath,mode='r',encoding='utf-8') as file:
        api_data=json.load(file)
        return api_data         #api_data['results']


def prepare_records(raw_response: list[dict],nested_field: str) -> list[dict]:
    records=[]
    if nested_field is None:
        return raw_response       
    for record in raw_response:
        record=record.copy()
        if not isinstance(record.get(nested_field), list):
            logger.warning(f"Missing or invalid type found for '{nested_field} in report {record.get('report_number')}")
            record[nested_field]=[]
        records.append(record)
    return records
    

def transform_events(raw_response:list[dict],expected_columns: list[str])-> pd.DataFrame:
    event_df=pd.DataFrame(raw_response)
    return event_df.reindex(columns=expected_columns)





def transform(raw_response:list[dict],expected_columns :list[str],required_cols:list[str],nested_field :str) -> pd.DataFrame:
    records=prepare_records(raw_response,nested_field)
    normalized_df=pd.json_normalize(records,record_path=nested_field,meta=["report_number"])
    if normalized_df.empty:
        return pd.DataFrame(columns=expected_columns)
    validate_schema(normalized_df,required_cols)
    return normalized_df.reindex(columns=expected_columns)



def validate_schema(df : pd.DataFrame, expected_columns : list[str]):
    actual_cols=set(df.columns)
    expected_cols=set(expected_columns)
    if (expected_cols-actual_cols):
        raise ValueError(f"schema validation error, missing columns {expected_cols-actual_cols}")




def validate_required_fields(df: pd.DataFrame,required_columns: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:

    empty_string_mask = pd.concat([df[col].astype("string").str.strip().eq("") for col in required_columns],axis=1)
    missing_fields_mask = (df[required_columns].isna() | empty_string_mask)
    invalid_row_mask = missing_fields_mask.any(axis=1)
    missing_columns = missing_fields_mask.apply(
        lambda row: row[row].index.tolist(),
        axis=1
    )
    invalid_rows_df=df[invalid_row_mask].copy()
    invalid_rows_df['missing_columns']=missing_columns[invalid_row_mask]

    valid_rows_df=df[~invalid_row_mask]
    
    return valid_rows_df,invalid_rows_df