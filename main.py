from src.logger import configure_logging,get_logger
from src.config import load_yaml_config,validate_api_config
from src.api_client import get_api_data
from src.writer import save_response

configure_logging()
logger=get_logger(__name__)



api_config=load_yaml_config('configs/settings.yaml')
validate_api_config(api_config)
api_response = get_api_data(url=api_config['api']['base_url'],api_config=api_config['api'],parameters={"limit" : 5})
file_name=save_response(response=api_response,output_dir=api_config['paths']['raw_data'])


