from pathlib import Path
import pandas as pd
from src.transformer import transform,validate_required_fields
from src.writer import save_response
import uuid
from datetime import datetime
current_day=datetime.now().strftime('%Y-%m-%d')


def process_entity(
        valid_results:list[dict],
        entity_schema:list[str],
        quarantine_directory:Path,
        processed_directory: Path,
        nested_field:str,
        entity_name :str,
        run_id : uuid
        ) -> pd.DataFrame:
    columns = entity_schema['columns']
    required = entity_schema['required']

    
    df=transform(raw_response=valid_results,nested_field=nested_field,expected_columns=columns,required_cols=required)
    valid_df,invalid_df=validate_required_fields(df,required)
    if not invalid_df.empty:
        save_response(response=invalid_df,output_dir=quarantine_directory / entity_name / current_day ,file_prefix=f'fda_{entity_name}_')
    valid_df['ingestion_id']=str(run_id)
    file_path=save_response(response=valid_df,output_dir=processed_directory /entity_name /current_day ,file_prefix=f'fda_{entity_name}_')
    return valid_df



  