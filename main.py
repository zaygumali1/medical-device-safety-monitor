from src.logger import configure_logging,get_logger
from src.config import load_yaml_config,validate_api_config
from src.api_client import get_api_data
from src.writer import save_response
from src.query_builder import build_api_parameters
from src.transformer import load_raw_response,transform_devices,transform_events,transform_mdr_text,transform_patients,validate_schema

configure_logging()
logger=get_logger(__name__)



api_config=load_yaml_config('configs/settings.yaml')
validate_api_config(api_config)
params=build_api_parameters(api_config)







api_response = get_api_data(url=api_config['api']['base_url'],api_config=api_config['api'],parameters=params)
event_file_path=save_response(response=api_response,output_dir=api_config['paths']['raw_data'],file_prefix='fda_events_')
response=load_raw_response(event_file_path)
results = response["results"]


df_events=transform_events(results)

df_devices=transform_devices(results)
device_file_path=save_response(response=df_devices,output_dir=api_config['paths']['proceesed'] + '/devices'  ,file_prefix='fda_devices_')


df_patients=transform_patients(results)
patients_file_path=save_response(response=df_patients,output_dir=api_config['paths']['proceesed'] + '/patients'  ,file_prefix='fda_patients_')

df_mdr_texts=transform_mdr_text(results)
mdr_text_file_path=save_response(response=df_mdr_texts,output_dir=api_config['paths']['proceesed'] + '/mdr_texts'  ,file_prefix='fda_mdrtexts_')






