import json
import time
from pathlib import Path
from datetime import datetime


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


def get_web_content_long_str(json_key_path):
    """get_web_content_long_str Get value from a json object by key that present in json_key_path.
        :param json_key_path: key path of json object
        :return: long string concatenated from a json array"""
    web_content = get_web_content()  # Get web context json file
    for item in json_key_path:  # Get value from a json object by key that present in json_key_path
        web_content = web_content[item]
    return concatenate_list_to_one_str(web_content)  # Concatenate long string from a json array of strings


def print_divider(div_type):  # for example, div_type="*" or "-"

    print(div_type * 91, flush=True)


def print_json(json_object):  # Printout JSON object in proper coding (Chinese problem etc.)
    json_string = json.dumps(json_object, ensure_ascii=False, indent=4, default=str).encode('utf8')
    print(json_string.decode(), flush=True)


def json_to_beauty_str(json_object):  # Printout JSON object in proper coding (Chinese problem etc.)
    json_string = json.dumps(json_object, ensure_ascii=False, indent=4, default=str).encode('utf8')
    return json_string.decode()


def pause(pause_string: str):
    wait = input(pause_string)


def print_df(df):
    print(df.to_string)
    print_divider(".")


def is_float(string):
    try:
        return float(string) and '.' in string  # True if a string is a number contains a dot
    except ValueError:  # String is not a number
        return False


def concatenate_list_to_one_str(list_of_strings):
    result_str = ""
    for list_str in list_of_strings:
        result_str += str(list_str)

    return result_str


def sort_list_of_dict_by_key(dict_to_sort: list, sort_key: str, sort_type: str = "ASC") -> list:
    """
    function sorting LIST of DICTIONARY objects, based on an object key and sorting type.
    :param dict_to_sort: LIST of DICTIONARY objects
    :param sort_key: object key
    :param sort_type: sorting type ASC or DESC [optional], default ASC
    :return: sorted LIST of DICTIONARY objects
    """

    if sort_type == "ASC":  # Ascending order
        reverse = False
    elif sort_type == "DESC":  # Descending order
        reverse = True
    else:
        reverse = False  # Ascending order

    sorted_dict = sorted(dict_to_sort, key=lambda x: x[sort_key], reverse=reverse)

    return sorted_dict


def mark_sub_string(string: str, sub_string: str, mark_start: str, mark_end: str, case: bool = False) -> str:
    def find_index():
        if case:  # Case-sensitive search
            return string.find(sub_string)
        else:  # Case-insensitive search
            return string.lower().find(sub_string.lower())

    index = find_index()
    if index == -1:  # sub_string is not found in string
        return string

    # Marking string by mark_start before sub_string
    sub_string_original = string[index:index + len(sub_string)]
    string = string[:index] + mark_start + sub_string_original + string[index + len(sub_string):]

    # Marking string by mark_end after sub_string
    index = find_index()
    marked_string = string[:index + len(sub_string)] + mark_end + string[index + len(sub_string):]

    return marked_string


"Logging and error handling: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"


def log_endpoint_requests(payload_json, response_json):
    log_json = {
        "json_rpc_api": f"Request date/time: {get_current_time_utc('TIME')}",
        "payload_json": payload_json,
        "response_json": response_json
    }
    print_json(log_json)
    # Add logging HERE ->


def exception_handler(proj_file, func_name, exception_error):
    exception_error_json = {
        "server_exception_date": get_current_time_utc("TIME"),
        "server_exception_file": proj_file,
        "server_exception_func": func_name,
        "server_exception_error": exception_error
    }
    print_json(exception_error_json)
    # Add logging HERE ->


def print_and_log_request_errors(check_result, request_headers, request_payload):
    json_string = json.dumps(check_result["response_json"], ensure_ascii=False, indent=4, default=str).encode('utf8')
    print_and_log_string = f"""{'!' * 91}
{get_current_time_utc('TIME')} - api endpoint ERROR
Request header(s):" {request_headers}
Request payload: {request_payload}
Customer response:
{json_string.decode()}
{'^' * 91}"""
    print(print_and_log_string)
