import os
import zipfile
import json
import io
import requests
import json

def get_alfresco_config():
    """Obtain Alfresco configuration from config file"""
    path_to_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
    with open(path_to_json, "r") as file:
        config_file = json.load(file)
    alfresco_config = config_file["ALFRESCO"]
    return alfresco_config

def evaluate_response(status_code, response):
    """Evaluate API response http codes"""
    response_dict = format_response(status_code, response)

    if status_code not in [200, 202]:
        print('Error in request')
        print(response_dict)

    return response_dict

def format_response(status_code, response):
    """Format response in dict"""
    return {'status_code': status_code, 'response': response}

def delete_zip_file(file_name):
    """Delete zip file"""
    if os.path.exists(file_name):
        os.remove(file_name)
    print(f'Deleting file {file_name}')

def extract_zip_content(zip_content):
    """Extract all contents of zip file"""
    alfresco_config = get_alfresco_config()
    file_name = alfresco_config['FOLDER_NAME'] + '.zip'
    print(f'Extracting content from file: {file_name}')
    zip = zipfile.ZipFile(io.BytesIO(zip_content))
    zip.extractall(alfresco_config['DOWNLOAD_FOLDER_PATH'])
    delete_zip_file(file_name)
    
def post_request(url, body, headers):
    """Function to make a POST request with body"""
    try:
        alfresco_config = get_alfresco_config()
        response = requests.post(url, auth=(alfresco_config['API_USER'], alfresco_config['API_PASS']), headers=headers, data=body, verify=False, timeout=alfresco_config['TIMEOUT'])
        response.raise_for_status()

    except requests.exceptions.Timeout as timeout:
        return format_response(500, str(timeout))
    except requests.exceptions.RequestException as exception:
        return format_response(500, str(exception))
    except Exception as err:
        return format_response(500, str(err))
    
    data = evaluate_response(response.status_code, response.json())

    return data

def get_request(url, payload, is_stream=False):
    """Function to make a GET request to obtain API data"""
    headers = {"content-type": "application/json"}

    try:
        alfresco_config = get_alfresco_config()
        response = requests.get(url, auth=(alfresco_config['API_USER'], alfresco_config['API_PASS']), headers=headers, params=payload, stream=is_stream, verify=False, timeout=alfresco_config['TIMEOUT'])
        response.raise_for_status()

    except requests.exceptions.Timeout as timeout:
        return format_response(500, str(timeout))
    except requests.exceptions.RequestException as exception:
        return format_response(500, str(exception))
    except Exception as err:
        return format_response(500, str(err))

    if not is_stream:
        data = evaluate_response(response.status_code, response.json())
    else:
        extract_zip_content(response.content)
        data = evaluate_response(response.status_code, {})

    return data

def get_folder_id():
    """Obtain folder id in Alfresco with CMIS query"""
    alfresco_config = get_alfresco_config()
    cmis_endpoint = '/cmis/versions/1.1/browser'
    url = alfresco_config['URL'] + cmis_endpoint
    query = f"select * from cmis:folder where cmis:name = '{alfresco_config['FOLDER_NAME']}' and cmis:objectTypeId = 'cmis:folder'"
    body = {
        'cmisaction':'query',
        'statement': query,
        'succinct':'true'
    }
    headers = {'Content-Type':'application/x-www-form-urlencoded'}

    response = post_request(url, body, headers)

    if response["status_code"] != 200:
        return

    num_folders = response["response"]["numItems"]
    
    if num_folders != 1:
        print(f'{num_folders} folders where found with name {alfresco_config["FOLDER_NAME"]}')
        return
    
    folder_id = response["response"]["results"][0]["succinctProperties"]["cmis:objectId"]

    return folder_id

def process_download(id):
    """Download element in zip file by id"""
    alfresco_config = get_alfresco_config()
    url = alfresco_config['URL'] + alfresco_config['DOWNLOADS_ENDPOINT']
    body = json.dumps({"nodeIds":[ str(id) ]})
    headers = {"content-type": "application/json"}

    response = post_request(url, body, headers)

    return response

def get_download_status(id):
    """Get download status after requesting download"""
    alfresco_config = get_alfresco_config()
    url = alfresco_config['URL'] + alfresco_config['DOWNLOADS_ENDPOINT'] + id
    payload = {}
    status = 'ERROR'

    response = get_request(url, payload)

    if response['status_code'] == 200:
        status = response['response']['entry']['status']
    else:
        print(f'Error obtaining download status')
        
    return status

def get_download_content(id):
    """Get download content after zip file is complete"""
    alfresco_config = get_alfresco_config()
    endpoint = '/alfresco/versions/1/nodes/'
    url = alfresco_config['URL'] + endpoint + id + '/content'
    payload = {}
    is_stream = True

    response = get_request(url, payload, is_stream)

    return response