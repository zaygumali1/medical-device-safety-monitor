from src.logger import configure_logging,get_logger
from src.config import load_yaml_config,validate_api_config
from src.api_client import get_api_data
from src.writer import save_response
from src.query_builder import build_api_parameters
from src.transformer import (load_raw_response,transform_events,
                             validate_required_fields)
from src.pipeline import process_entity
from pathlib import Path
import uuid
configure_logging()
logger=get_logger(__name__)
ingestion_id=uuid.uuid4()

api_config=load_yaml_config('configs/settings.yaml')
validate_api_config(api_config)
SCHEMAS=api_config.get("schemas")
processed_path=Path(api_config['paths']['processed'])
quarantine_path=Path(api_config['paths']['quarantine'])


params=build_api_parameters(api_config)
api_response = get_api_data(url=api_config['api']['base_url'],api_config=api_config['api'],parameters=params)
event_file_path=save_response(response=api_response,output_dir=api_config['paths']['raw_data'],file_prefix='fda_events_')
response=load_raw_response(event_file_path)
results = response["results"]





df_events=transform_events(results,SCHEMAS["events"]["columns"])
df_valid_events,df_quarantine_events=validate_required_fields(df_events,SCHEMAS["events"]["required"])
valid_results=[record for record in results if record["report_number"] in df_valid_events['report_number'].unique()]

if not df_quarantine_events.empty:
    quarantine_events=save_response(response=df_quarantine_events,output_dir=quarantine_path / 'events'  ,file_prefix='fda_events_')

df_events=process_entity(
    valid_results=valid_results,
    entity_schema=SCHEMAS["events"],
    quarantine_directory=quarantine_path,
    processed_directory=processed_path,
    nested_field=None,
    entity_name="events",
    run_id=ingestion_id
    )

df_devices=process_entity(
    valid_results=valid_results,
    entity_schema=SCHEMAS["devices"],
    quarantine_directory=quarantine_path,
    processed_directory=processed_path,
    nested_field='device',
    entity_name="devices",
    run_id=ingestion_id
    )

df_patients=process_entity(
    valid_results=valid_results,
    entity_schema=SCHEMAS["patients"],
    quarantine_directory=quarantine_path,
    processed_directory=processed_path,
    nested_field='patient',
    entity_name="patients",
    run_id=ingestion_id
    )

df_mdr_texts=process_entity(
    valid_results=valid_results,
    entity_schema=SCHEMAS["mdr_text"],
    quarantine_directory=quarantine_path ,
    processed_directory=processed_path,
    nested_field='mdr_text',
    entity_name="mdr_texts",
    run_id=ingestion_id
    )



