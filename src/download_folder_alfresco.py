import traceback
import time
import utils.utils as utils


def download_alfresco_folder():
    """Download data folder from Alfresco API"""
    start_time = time.time()

    try:
        print(f'Obtaining Alfresco folders...')
        folders = utils.get_folders()
        folder_num = 1
        total_folders = len(folders)

        for folder in folders:
            print(f'Downloading folder {folder_num}/{total_folders}...')
            print(f'Obtaining Alfresco folder id for folder {folder_num}...')
            folder_id = folder["succinctProperties"]["cmis:objectId"]
            if not folder_id:
                print(f'Error obtaining Alfresco folder id', 'critical')
                return

            print(f'Alfresco folder id obtained: {folder_id}')
            print(f'Requesting folder download')

            response = utils.process_download(folder_id)

            if response['status_code'] != 202:
                print(f'Error obtaining download')
                return

            download_id = response['response']['entry']['id']
            print(f'Download requested with id: {download_id}')

            status = utils.get_download_status(download_id)
            print(f'Download status {status}')

            while status in ['IN_PROGRESS', 'PENDING']:
                time.sleep(5)
                status = utils.get_download_status(download_id)
                print(f'Download status {status}')

            print(f'Download generated, getting content...')
            response = utils.get_download_content(download_id, folder_num)

            if response['status_code'] != 200:
                print(f'Error obtaining download')
                return

            print(f'Download {folder_num}/{total_folders} complete!')
            folder_num += 1

    except Exception as error:
        print("Unexpected error: " + str(error))
        print(traceback.format_exc())

    finally:
        # Calculate execution time
        exec_time = (time.time() - start_time)
        print('Data transfer from API took ' + str(round(exec_time)) + 's.')


if __name__ == '__main__':
    download_alfresco_folder()
