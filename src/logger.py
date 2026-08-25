import logging
from pathlib import Path
from datetime import datetime

timestamp=datetime.now().strftime("%Y%m%d%H%M%S")
ROOT_DIR=Path(__file__).resolve().parent.parent
LOG_DIR=ROOT_DIR /"logs"
LOG_DIR.mkdir(parents=True,exist_ok=True)
LOG_FILE=LOG_DIR/f"api_log_{timestamp}.log"



def configure_logging():
     logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s |%(name)s |%(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(LOG_FILE)
            ]
        )



def get_logger(name):
    return logging.getLogger(name)