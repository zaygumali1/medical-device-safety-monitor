from pathlib import Path
import yaml

ROOT_DIR=Path(__file__).parent.parent.resolve()

def load_yaml_config(path : str) -> dict:
    file_path=ROOT_DIR / path
    try:
        with open(file=file_path,mode='r',encoding='utf-8') as file :
            contents=yaml.safe_load(file)
        if contents is None:
            raise ValueError(f"Configuration file is empty: {file_path}")
        if not isinstance(contents,dict):
            raise TypeError(f"Configuration must be a dictionary : {file_path}")
        return contents
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
def validate_api_config(config: dict) -> None:
    if "api" not in config or not isinstance(config, dict):
        raise ValueError("API configuration issue")


    if not isinstance(config["api"], dict):
        raise ValueError("API configuration must be a dictionary")

    api_config = config["api"]


    if (
        "timeout" not in api_config
        or not isinstance(api_config["timeout"], int)
        or isinstance(api_config["timeout"], bool)
        or api_config["timeout"] <= 0
    ):
        raise ValueError("Invalid timeout configuration")

    
    if (
        "max_attempts" not in api_config
        or not isinstance(api_config["max_attempts"], int)
        or isinstance(api_config["max_attempts"], bool)
        or api_config["max_attempts"] < 1
    ):
        raise ValueError("Invalid max_attempts configuration")


    if (
        "max_retry_delay" not in api_config
        or not isinstance(api_config["max_retry_delay"], int)
        or isinstance(api_config["max_retry_delay"], bool)
        or api_config["max_retry_delay"] < 0
    ):
        raise ValueError("Invalid max_retry_delay configuration")