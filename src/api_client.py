import time
import requests


RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 5
REQUEST_TIMEOUT = 30
MAX_RETRY_DELAY = 30

def get_api_data(url:str,parameters:dict):
    attempts=1
    while attempts<=MAX_ATTEMPTS:
        try:
            response=requests.get(url=url,params=parameters,timeout=REQUEST_TIMEOUT)
            server_retry_time=response.headers.get("Retry-After",None)

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
        except ValueError:
            server_retry_delay=None       
        delay =min(server_retry_delay if server_retry_delay is not None  else 2**(attempts-1),MAX_RETRY_DELAY)
        time.sleep(delay)
        attempts+=1





       