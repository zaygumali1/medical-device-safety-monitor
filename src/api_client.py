from src.logger import get_logger
import time
import requests

logger=get_logger(__name__)

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

def get_api_data(url:str,api_config:dict,parameters:dict|None=None):

    MAX_ATTEMPTS    = api_config["max_attempts"]
    REQUEST_TIMEOUT = api_config["timeout"]
    MAX_RETRY_DELAY = api_config["max_retry_delay"]

    attempts=1
    while attempts<=MAX_ATTEMPTS:
        server_retry_delay = None
        try:
            response=requests.get(url=url,params=parameters,timeout=REQUEST_TIMEOUT)
            server_retry_delay=response.headers.get("Retry-After",None)
            

            if response.ok:
                return response.json()

            if response.status_code not in RETRY_STATUS_CODES:
                response.raise_for_status()

            logger.warning(f"API request returned HTTP {response.status_code}.")

            if MAX_ATTEMPTS==attempts:
                logger.error(f"API request failed after {MAX_ATTEMPTS} attempts. "f"HTTP status: {response.status_code}.")
                response.raise_for_status()
            

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as ex:
            if attempts==MAX_ATTEMPTS:
                logger.error(f"API request failed with {type(ex).__name__}: {ex}")
                raise
                


        

        if server_retry_delay is not None:
            logger.info(f"Server provided Retry-After: {server_retry_delay} seconds.")


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




       