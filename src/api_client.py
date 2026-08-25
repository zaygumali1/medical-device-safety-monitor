from src.config import load_yaml_config, validate_api_config
from src.logger import configure_logging,get_logger
import time
import requests


config = load_yaml_config("configs/settings.yaml")
validate_api_config(config)
configure_logging()
logger=get_logger(__name__)

API_CONFIG = config["api"]
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = API_CONFIG["max_attempts"]
REQUEST_TIMEOUT = API_CONFIG["timeout"]
MAX_RETRY_DELAY = API_CONFIG["max_retry_delay"]

def get_api_data(url:str,parameters:dict):
    attempts=1
    while attempts<=MAX_ATTEMPTS:
        try:
            response=requests.get(url=url,params=parameters,timeout=REQUEST_TIMEOUT)
            

            if response.ok:
                return response.json()

            if response.status_code not in RETRY_STATUS_CODES:
                response.raise_for_status()

            if MAX_ATTEMPTS==attempts:
                response.raise_for_status()
            

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout):
            if attempts==MAX_ATTEMPTS:
                raise
        
        server_retry_delay=response.headers.get("Retry-After",None)

        try:
            server_retry_delay=int(server_retry_delay)
            if server_retry_delay < 1:
                raise ValueError
        except (ValueError,TypeError):
            server_retry_delay=None       


        delay =min(server_retry_delay if server_retry_delay is not None  else 2**(attempts-1),MAX_RETRY_DELAY)
        time.sleep(delay)
        attempts+=1
        
        logger.warning(
            f"API request failed. Retrying attempt {attempts} "
            f"of {MAX_ATTEMPTS} after {delay} seconds."
        )




       