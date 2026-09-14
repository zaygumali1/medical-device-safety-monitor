def build_api_parameters(api_config:dict)-> dict:
    return {
    "search": f'device.device_report_product_code:({" OR ".join(api_config["product_codes"])})',
    "limit" :api_config['api']["limit"]
    }           
