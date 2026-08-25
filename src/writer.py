import json
from pathlib import Path
from datetime import datetime
from src.logger import get_logger
ROOT_DIR=Path(__file__).resolve().parent.parent

logger=get_logger(__name__)

def save_response(response:dict, output_dir: Path):
    output_dir=ROOT_DIR /output_dir
    output_dir.mkdir(parents=True,exist_ok=True)
    file_name=f"fda_events_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path=output_dir/f"{file_name}"
    with open(file=output_path,mode='w',encoding='utf-8') as f:
        json.dump(response,f,indent=4)
    logger.info(f"Raw API response saved to {output_path}")
    return output_path



