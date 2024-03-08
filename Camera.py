import sys
import os
os.environ["PYLON_CAMEMU"] = "3"
from pypylon import pylon
from pypylon import genicam
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
import time
import base64
from websocket_server import WebsocketServer
import threading
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import json
from datetime import datetime


from lib.logging.logging import rollgap_logging
from lib.config.config import rollgap_config
from lib.Restart.restart_program import restart_program 



rollgap_logging_instance = rollgap_logging()
rollgap_config_instance = rollgap_config()






def grabresult_to_opencv_image(grabResult):
    try:
        image = grabResult.GetArray()
        # print(type(image))
        return image
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)
        return None

def image_to_base64(grabResult, pixelMax):
    try:
        #
        image = grabresult_to_opencv_image(grabResult)
        #
        # if image is not None and image.max() > pixelMax:
        if image is not None :
            _, buffer = cv2.imencode('.png', image)
            img_str = base64.b64encode(buffer)
            return img_str.decode('utf-8')
        else:
            pass
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)





def on_disconnect(client, userdata, rc):
    try:
        if rc != 0:
            rollgap_logging_instance.logMsg_Error("Unexpected disconnection. Reconnecting...", rc)
            client.reconnect()
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)



def on_connect(client, userdata, flags, rc):
    try:
        client.subscribe(SUB_TOPIC, 0)
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)




def on_message(client, userdata, msg, pub_topic_cam, led_1Ch_Value, led_2Ch_Value, led_intensity_min, os_pixelMax, ds_pixelMax):
    try:
        if msg is not None:
            data = json.loads(msg.payload)
            #
            led1_intensity = data[led_1Ch_Value]
            led2_intensity = data[led_2Ch_Value]
            #
            # Grab and process image from os_camera
            if int(led1_intensity) > led_intensity_min:
                process_camera(0, pub_topic_cam, os_pixelMax)
            # Grab and process image from ds_camera
            elif int(led2_intensity) > led_intensity_min:
                process_camera(1, pub_topic_cam, ds_pixelMax)

            
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)


def mqtt_Config(mqtt_broker_ip, pub_topic_cam, sub_topic_LED, led_1Ch_Value, led_2Ch_Value, led_intensity_min, os_pixelMax, ds_pixelMax):
    try:
        #
        # global MQTT_BROKER, PUB_TOPIC1, PUB_TOPIC2, PUB_TOPIC3, SUB_TOPIC, client
        global SUB_TOPIC, client
        MQTT_BROKER = mqtt_broker_ip
        PUB_TOPIC = pub_topic_cam
        SUB_TOPIC = sub_topic_LED
        print(f'  1. MQTT_BROKER = {MQTT_BROKER}')
        print(f'  2. PUB_TOPIC = {PUB_TOPIC}')
        print(f'  3. SUB_TOPIC = {SUB_TOPIC}')
        #
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg, pub_topic_cam, led_1Ch_Value, led_2Ch_Value, led_intensity_min, os_pixelMax, ds_pixelMax)

        result = ''.join(filter(str.isdigit, led_1Ch_Value))
        result2 = ''.join(filter(str.isdigit, led_2Ch_Value))

        print(f'  4. LED_Set =  OS: {result}ch / DS: {result2}ch')
        print(f'  5. LED_intensity_min = {led_intensity_min}')
        print(f'  6. pixelMax = OS: {os_pixelMax} / DS: {ds_pixelMax}')
        client.connect(MQTT_BROKER, 1883, 60)
        #
        
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

def config():
    try:
        #
        current_script_path = os.path.basename(__file__)
        current_script_name, _ = os.path.splitext(os.path.basename(current_script_path))
        # print(f"== The current script file name ==\n  -{current_script_path}\n")
        #
        rollgap_logging_instance.logFileCreate(current_script_name)
        #
        #
        config_folder_path = "./system_config"
        config_file_path = f'{config_folder_path}/rollgap_config.json'
        # 
        if not os.path.exists(config_folder_path):
            os.makedirs(config_folder_path)
            rollgap_config_instance.rollgap_config_create(config_file_path)
        else:
            # 
            if not os.path.isfile(config_file_path):
                rollgap_config_instance.rollgap_config_create(config_file_path)
            else:
                #
                with open(config_file_path, 'r') as json_file:        
                    config = json.load(json_file) #loads load 차이
                #
                print('== Reading the config file... ==')
          
                ##[Mqtt_Config]
                mqtt_broker_ip = config["Mqtt_Config"]["mqtt_broker_ip"]
                pub_topic_cam = config["Mqtt_Config"]["pub_topic_cam"]
                sub_topic_LED = config["Mqtt_Config"]["sub_topic_LED"]
                
                ##[LED_Config]
                led_1Ch_Value = config["led_config"]["os_set_led_Ch"]
                if led_1Ch_Value == 1:
                    led_1Ch_Value = "led1_intensity"
                elif led_1Ch_Value == 2:
                    led_1Ch_Value = "led2_intensity"
                else:
                    led_1Ch_Value = "led2_intensity"
                #
                led_2Ch_Value = config["led_config"]["ds_set_led_Ch"]
                if led_2Ch_Value == 1:
                    led_2Ch_Value = "led1_intensity"
                elif led_2Ch_Value == 2:
                    led_2Ch_Value = "led2_intensity"
                else:
                    led_2Ch_Value = "led1_intensity"
                #
                led_intensity_min = config["led_config"]["led_intensity_min"]
                if led_intensity_min > 999:
                    led_intensity_min = 999
                elif led_intensity_min <= 0:
                    led_intensity_min = 0

                ##[imagePixelMax]
                os_pixelMax = config["imagePixelMax"]["os_pixelMax"]
                if os_pixelMax > 200:
                    os_pixelMax = 200
                elif os_pixelMax <= 0 :
                    os_pixelMax = 0

                ds_pixelMax = config["imagePixelMax"]["ds_pixelMax"]
                if ds_pixelMax > 200:
                    ds_pixelMax = 200
                elif ds_pixelMax <= 0 :
                    ds_pixelMax = 0


                ####[CameraSetting]
                maxCamerasToUse = config["Camera_Setting"]["maxCamerasToUse"]
                camera_settings = []
                for camera_idx in range(1, maxCamerasToUse + 1):
                    camera_settings.append(config["Camera_Setting"][str(camera_idx)])


                ##[return]
                return config_file_path, mqtt_broker_ip, pub_topic_cam, sub_topic_LED, led_1Ch_Value, led_2Ch_Value, led_intensity_min, os_pixelMax, ds_pixelMax, maxCamerasToUse, camera_settings
    #
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

def cameraSetting(maxCamerasToUse, camera_settings):
    try:
        #
        #
        tlFactory = pylon.TlFactory.GetInstance()
        #
        devices = tlFactory.EnumerateDevices()
        lenDevices = len(devices)
        print(f'  8. Camera {lenDevices}ea')
        #
        if lenDevices == 0:
            raise pylon.RuntimeException("No camera present.")
        #            
        elif lenDevices >=1 :                
            #
            print("\n== Current Device List ==")
            #
            for i in range(lenDevices):
                print(f'  No.{i+1} : {devices[i].GetUserDefinedName()},  {devices[i].GetModelName()}')
            #
            #
            global cameras
            cameras = pylon.InstantCameraArray(min(lenDevices, maxCamerasToUse))
            # l = cameras.GetSize()
            #
            #
            print("\n== Selected Device Data ==")
            for idx, (cam, camera_setting) in enumerate(zip(cameras, camera_settings)):
                cam.Attach(tlFactory.CreateDevice(devices[idx]))
                ###[set Value]
                set_ExposureTime = max(2, min(10000000, camera_settings[idx].get("set_ExposureTime", 2)))
                set_BslBrightness = max(-1, min(1, camera_settings[idx].get("set_BslBrightness", 0)))
                set_BslContrastMode = "Linear" if camera_settings[idx].get("set_BslContrastMode", "L") == "L" else "SCurve"
                set_BslContrast = max(-1, min(1, camera_settings[idx].get("set_BslContrast", 0)))
                set_BslSharpnessEnhancement = max(1, min(3.984375, camera_settings[idx].get("set_BslSharpnessEnhancement", 2.0)))
                set_BslNoiseReduction = max(1, min(2, camera_settings[idx].get("set_BslNoiseReduction", 1.0)))
                set_TriggerSelector = camera_settings[idx].get("set_TriggerSelector", "FrameStart")
                set_TriggerSource = camera_settings[idx].get("set_TriggerSource", "Software")
                set_TriggerMode = camera_settings[idx].get("set_TriggerMode", "On")
                ####[Camera Setting]
                cam.Open()
                # Set the exposure time to 0000 microseconds
                cam.ExposureTime.SetValue(set_ExposureTime) 
                # Set the Brightness parameter
                cam.BslBrightness.SetValue(set_BslBrightness) 
                # Set the contrast mode to Linear
                cam.BslContrastMode.SetValue(set_BslContrastMode)
                # Set the Contrast parameter to 1.2s
                cam.BslContrast.SetValue(set_BslContrast) 
                # Configure improved sharpness
                cam.BslSharpnessEnhancement.SetValue(set_BslSharpnessEnhancement)
                # Configure noise reduction
                cam.BslNoiseReduction.SetValue(set_BslNoiseReduction)
                # camera.TriggerSelector.SetValue("FrameStart")
                cam.TriggerSelector.SetValue(set_TriggerSelector)
                # camera.TriggerSource.SetValue("Software")
                cam.TriggerSource.SetValue(set_TriggerSource)
                # camera.TriggerMode.SetValue("On")
                cam.TriggerMode.SetValue(set_TriggerMode)
                #
                print(f"  No. {idx+1}: Camera Id=[ {devices[idx].GetUserDefinedName()} ],  Camera Model=[ {cam.GetDeviceInfo().GetModelName()} ], << Setting Done. >>")
                #
            #
            #
            #
            cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
            #
            #
        else:
            rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", f"!! Not found Cameras !!")
                
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)





# # #
# global image_window, image_window2
# image_window = pylon.PylonImageWindow()
# image_window.Create(1)
# image_window2 = pylon.PylonImageWindow()
# image_window2.Create(2)

def process_camera(cam_index, pub_topic_name, pixel_max):
    try:
        # start_time = time.time()
        time.sleep(0.1)  
        if cameras[cam_index].WaitForFrameTriggerReady(pylon.TimeoutHandling_ThrowException, 5000):
            cameras[cam_index].ExecuteSoftwareTrigger()
            grabResult = cameras[cam_index].RetrieveResult(3000, pylon.TimeoutHandling_ThrowException)
            
            if grabResult.GrabSucceeded():
                latest_image = image_to_base64(grabResult, pixel_max)
                # print(latest_image)
                # print(type(latest_image)) #str


                # # #test
                # if cam_index ==0:
                #     # print("오예스")
                #     image_window.SetImage(grabResult)
                #     image_window.Show()
                # else:
                #     # print("디예스")
                #     image_window2.SetImage(grabResult)
                #     image_window2.Show()
                # ##
                
                ####
                if latest_image is not None:
                    if cam_index ==0:
                        image_data = {
                            "side": "OS",
                            "image": latest_image
                        }
                    else:
                        image_data = {
                            "side": "DS",
                            "image": latest_image
                        }
                    response_json = json.dumps(image_data)
                    client.publish(pub_topic_name, response_json)
                else:
                    rollgap_logging_instance.logMsg_Error("process_camera Error: ", grabResult.ErrorCode)
                    

            grabResult.Release()
            # triggerTime = time.time() - start_time
            # print(f"cam_{cam_index+1} trigger Test = {triggerTime}")
                
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)





if __name__ == "__main__":
    try:
        

        
        (config_file_path,
            mqtt_broker_ip, pub_topic_cam, 
                sub_topic_LED, led_1Ch_Value, led_2Ch_Value, 
                    led_intensity_min, os_pixelMax, ds_pixelMax,
                        maxCamerasToUse, camera_settings) = config()
       
        mqtt_Config(mqtt_broker_ip, pub_topic_cam, sub_topic_LED, led_1Ch_Value, led_2Ch_Value, led_intensity_min, os_pixelMax, ds_pixelMax)
        

        config_watch_thread = threading.Thread(target=rollgap_config_instance.watch_config_changes, args=(config_file_path,))
        config_watch_thread.start()
        

        cameraSetting(maxCamerasToUse, camera_settings) 
        

        print(f'\n== Start ==')
        client.loop_forever()
        



        if not client.is_connected():
            rollgap_logging_instance.logMsg("MQTT client is not connected. Reconnecting...")
            client.reconnect()
        



        cameras.StopGrabbing()
        cameras.Close()
        

        rollgap_logging_instance.logMsg("  [Camera Close & Restart.]  ")
       

        restart_program()      

    except Exception as e:        
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)
        


        
