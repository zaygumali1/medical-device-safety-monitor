import json
from pathlib import Path
from datetime import datetime
from src.logger import get_logger
import pandas as pd
ROOT_DIR=Path(__file__).resolve().parent.parent

logger=get_logger(__name__)

def save_response(response:dict | pd.DataFrame , output_dir: Path,file_prefix:str):
    output_dir=ROOT_DIR /output_dir
    output_dir.mkdir(parents=True,exist_ok=True)
    file_name=f"{file_prefix}{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path=output_dir/f"{file_name}"
    with open(file=output_path,mode='w',encoding='utf-8') as f:
        if isinstance(response,dict):
            json.dump(response,f,indent=4)
        else:
            f.write(response.to_json(orient="records",indent=4))
            
    logger.info(f"{file_name} API response saved to {output_path}")
    return output_path



