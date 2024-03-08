import os
import datetime
import shutil
import time
import datetime

import threading
import json
import paho.mqtt.client as mqtt


from lib.config.config import rollgap_config
from lib.logging.logging import rollgap_logging
from lib.rollgap_DB.mariadbhandler import MariaDBHandler

rollgap_logging_instance = rollgap_logging()
rollgap_config_instance = rollgap_config()





def delete_old_folders_threaded(side, folder_path, days_threshold):
    current_date = datetime.datetime.now()

    try:
        # 폴더인지 확인
        if os.path.isdir(folder_path):
            # 폴더의 생성일을 얻어옴
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(folder_path))
            # 현재 날짜와 폴더 생성일 간의 차이를 계산
            days_since_creation = (current_date - creation_time).days
            # 지정된 날짜 이상 경과한 폴더는 삭제
            if days_since_creation >= days_threshold:
                shutil.rmtree(folder_path)
                rollgap_logging_instance.logMsg(f" {side} image Folder [{folder_path}] has been deleted.")

    except Exception as e:
        rollgap_logging_instance.logMsg_Error("delete_old_folders_threaded", e)





# def delete_old_folders_multi_threaded(side, directory_path, days_threshold=30):
#     threads = []
#     for folder_name in os.listdir(directory_path):
#         folder_path = os.path.join(directory_path, folder_name)
#         if os.path.isdir(folder_path):
#             thread = threading.Thread(target=delete_old_folders_threaded, args=(side, folder_path, days_threshold))
#             threads.append(thread)

#     for thread in threads:
#         thread.start()

#     for thread in threads:
#         thread.join()


def delete_old_folders_multi_threaded(side, directory_path, max_folders):
    try:
   

        folders = [os.path.join(directory_path, folder_name) for folder_name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder_name))]
        
        # 폴더가 max_folders보다 많으면 오래된 폴더부터 삭제
        if len(folders) > max_folders:
            sorted_folders = sorted(folders, key=os.path.getmtime)
            folders_to_delete = sorted_folders[:len(folders) - max_folders]

            for folder_path in folders_to_delete:
                shutil.rmtree(folder_path)
                rollgap_logging_instance.logMsg(f" {side} image Folder [{folder_path}] has been deleted.")
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("delete_old_folders_multi_threaded", e)









if __name__ == "__main__":



    config_folder_path = "./system_config"
    config_file_path = f'{config_folder_path}/rollgap_config.json'

    config = rollgap_config_instance.parse_json_config(config_file_path)

    max_folders = config["intThreshold"]["max_folders "]
    DS_imageSavePath = config["path"]["DS_imageSavePath"]
    OS_imageSavePath = config["path"]["OS_imageSavePath"]
    

    print(max_folders)

    while True:
        # Perform the deletion check once a day
        delete_old_folders_multi_threaded("DS", DS_imageSavePath, max_folders)
        delete_old_folders_multi_threaded("OS", OS_imageSavePath, max_folders)

        formatted_time =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Done, Time ={formatted_time}")
        # Sleep for 24 hours
        # time.sleep(24 * 60 * 60)  # 24 hours in seconds
        time.sleep(60)  # 24 hours in seconds





 경우에 따라 디비와 저장 파일을 지우는 코드를 DB.py에 합쳐 작성할 것.