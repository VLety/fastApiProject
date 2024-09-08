"""
Project name: REST API server solution based on FastAPI framework with RBAC model
Author: Volodymyr Letiahin
Contact: https://www.linkedin.com/in/volodymyr-letiahin-0208a5b2/
License: MIT
"""
import json
import time
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException

" Support functions ------------------------------------------------------------------------------------------------"
def get_project_root() -> Path:
    return Path(__file__).parent


def get_current_time_utc(date_format="DATE"):  # date_format = DATE or TIME or UNIX

    result = ""

    if date_format == "TIME":
        result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if date_format == "DATE":
        result = datetime.now().strftime("%Y-%m-%d")

    if date_format == "UNIX":
        result = int(time.time())  # current date and time in Unix timestamp format

    return result


def get_json_file_content(file_path):
    json_file = open(file_path, "r")  # Opening JSON file
    json_content = json.load(json_file)  # returns JSON object as parsed json content string
    json_file.close()  # Closing file

    return json_content


def get_setup() -> json:
    """ GET project setup from setup.json file"""
    file_path_config = f"{get_project_root()}/setup/setup.json"
    json_obj = get_json_file_content(file_path_config)

    return json_obj


def get_config():
    """ GET project config from config.json file"""
    file_path_config = f"{get_project_root()}/config/config.json"
    config_json = get_json_file_content(file_path_config)

    return config_json


def get_schemas():
    """ GET project schemas from schemas.json file"""
    file_path_config = f"{get_project_root()}/config/schemas.json"
    permissions_json = get_json_file_content(file_path_config)

    return permissions_json


def get_permissions():
    """ GET project permissions from permissions.json file"""
    file_path_config = f"{get_project_root()}/config/permissions.json"
    permissions_json = get_json_file_content(file_path_config)

    return permissions_json


def get_credential():
    """ GET project config from credential.json file"""
    file_path_config = f"{get_project_root()}/config/credential.json"
    credential_json = get_json_file_content(file_path_config)

    return credential_json


def get_web_content():
    """ GET project config from credential.json file"""
    file_path_config = f"{get_project_root()}/web/web_content.json"
    credential_json = get_json_file_content(file_path_config)

    return credential_json


def print_divider(div_type):  # for example, div_type="*" or "-"

    print(div_type * 91, flush=True)


def print_json(json_object):  # Printout JSON object in proper coding (Chinese problem etc.)
    json_string = json.dumps(json_object, ensure_ascii=False, indent=4, default=str).encode('utf8')
    print(json_string.decode(), flush=True)


def pause(pause_string: str):
    wait = input(pause_string)


def print_df(df):
    print(df.to_string)
    print_divider(".")


" Logging and error handling ---------------------------------------------------------------------------------------"


def raise_http_error(http_error_json: json, headers: json = None):
    status_code = http_error_json["status_code"]
    detail = http_error_json["detail"]
    if headers is None:
        raise HTTPException(status_code=status_code, detail=detail)
    else:
        raise HTTPException(status_code=status_code, detail=detail, headers=headers)
