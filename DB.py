import os
import sys
import json
import paho.mqtt.client as mqtt
from lib.logging.logging import rollgap_logging
from lib.config.config import rollgap_config
from lib.rollgap_DB.mariadbhandler import MariaDBHandler




rollgap_logging_instance = rollgap_logging()
rollgap_config_instance = rollgap_config()
saveOrder = "Off"




def on_disconnect(client, userdata, rc):
    try:
        if rc != 0:
            rollgap_logging_instance.logMsg("Unexpected disconnection. Reconnecting...", rc)
            client.reconnect()
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

def on_connect(client, userdata, flags, rc):
    try:
        # print("Connected with result code: "+str(rc))
        client.subscribe(SUB_TOPIC1,  0)
        client.subscribe(SUB_TOPIC2,  0)
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

def on_message(client, userdata, msg):
    try:
        #
        #
        data = msg.payload
        # print(data)
        topic = msg.topic
        #
        #
        if data is not None:
            if topic == SUB_TOPIC1:
                json_data = json.loads(data)
                global saveOrder
                saveOrder = json_data["Save_Data"]

            elif topic == SUB_TOPIC2:
                if saveOrder =="On":
                    insertDB(data)
                else:
                    pass

        else:
            print("Mqtt Data No!!!")

    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)




def insertDB(data):
    
    try:
        json_data = json.loads(data)
        camera_side = json_data["Camera_side"]
        point_data ={
            "TOP1": f'POINT({json_data["TOP1"][0]}, {json_data["TOP1"][1]})',
            "TOP2": f'POINT({json_data["TOP2"][0]}, {json_data["TOP2"][1]})',
            "TOP3": f'POINT({json_data["TOP3"][0]}, {json_data["TOP3"][1]})',
            "BTM1": f'POINT({json_data["BTM1"][0]}, {json_data["BTM1"][1]})',
            "BTM2": f'POINT({json_data["BTM2"][0]}, {json_data["BTM2"][1]})',
            "BTM3": f'POINT({json_data["BTM3"][0]}, {json_data["BTM3"][1]})',
            #
            "Distance_P1toP2": json_data["Distance_P1_P2"], 
            "Distance_P2toP3": json_data["Distance_P2_P3"], 
            "Distance_P3toP4": json_data["Distance_P3_B1"], 
            "Distance_P4toP5": json_data["Distance_B1_B2"], 
            "Distance_P5toP6": json_data["Distance_B2_B3"],  
            #
            "T1_T2_Mid":  f'POINT({json_data["T1_T2_Mid"][0]}, {json_data["T1_T2_Mid"][1]})',            
            "T3_B1_Mid":  f'POINT({json_data["T3_B1_Mid"][0]}, {json_data["T3_B1_Mid"][1]})',            
            "B2_B3_Mid":  f'POINT({json_data["B2_B3_Mid"][0]}, {json_data["B2_B3_Mid"][1]})',            
            "T2_B2_Mid":  f'POINT({json_data["T2_B2_Mid"][0]}, {json_data["T2_B2_Mid"][1]})',            
            #
            "dis_SegtoP1": json_data["dis_SegtoP1"],
            "dis_SegtoP2": json_data["dis_SegtoP2"],
            "dis_SegtoP3": json_data["dis_SegtoP3"],
            "dis_SegtoP4": json_data["dis_SegtoP4"],
            "dis_SegtoP5": json_data["dis_SegtoP5"],

            "image_Save_path": json_data["image_Save_path"],
        }

        # print( json_data["points_C_Roll"][0])
        # print( type(json_data["points_C_Roll"]))
        p1 = json_data["points_C_Roll"][0]
        p2 = json_data["points_C_Roll"][1]
        p3 = json_data["points_C_Roll"][2]
        p4 = json_data["points_C_Roll"][3]
        p5 = json_data["points_C_Roll"][4]
        p6 = json_data["points_C_Roll"][5]

        
              
        points_dict={
            "p1": f"({p1[0], p1[1]})",        
            "p2": f"({p2[0], p2[1]})",        
            "p3": f"({p3[0], p3[1]})",        
            "p4": f"({p4[0], p4[1]})",        
            "p5": f"({p5[0], p5[1]})",        
            "p6": f"({p6[0], p6[1]})",        
            
        }
        
        if camera_side == "OS":
            mariadbHandler.insert("os_data", point_data)
            mariadbHandler.insert("os_c_roll_seg", points_dict)     
            print("Done")       
        else:
            mariadbHandler.insert("ds_data", point_data)
            mariadbHandler.insert("ds_c_roll_seg", points_dict)

    except Exception as e:
       rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

        
       







def mqtt_Config(mqtt_broker_ip, Sub_ai_Res, sub_topic_saveMSG):
    
    try:
        #
        # MQTT Setup
        #
        global SUB_TOPIC1, SUB_TOPIC2, client
        
        MQTT_BROKER = mqtt_broker_ip
        
        SUB_TOPIC1 = sub_topic_saveMSG # 저장 명령
        SUB_TOPIC2 = Sub_ai_Res # 분석 Json
        #
        print(f'  1. MQTT_BROKER = {MQTT_BROKER}')
        print(f'  2. SUB_TOPIC1 = {SUB_TOPIC1}')
        print(f'  3. SUB_TOPIC2 = {SUB_TOPIC2}')
        #
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        client.connect(MQTT_BROKER, 1883, 60)
        
        #
        
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)



def config():
    try:
        #
        current_script_path = os.path.basename(__file__)
        current_script_name, _ = os.path.splitext(os.path.basename(current_script_path))
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
                config = rollgap_config_instance.parse_json_config(config_file_path)
                #
                print('== Reading the config file... ==')
                #
                mqtt_broker_ip = config["Mqtt_Config"]["mqtt_broker_ip"]
                #
                Sub_ai_Res = config["Mqtt_Config"]["pub_topic_ai_Res"]
                #
                sub_topic_saveMSG = config["Mqtt_Config"]["sub_topic_saveMSG"]
                #
                #
                mariadbHandler = MariaDBHandler(config)
                #
                return mqtt_broker_ip, Sub_ai_Res, sub_topic_saveMSG, mariadbHandler
        #
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)



if __name__ == "__main__":
    try:
        mqtt_broker_ip, Sub_ai_Res, sub_topic_saveMSG, mariadbHandler = config()

        mqtt_Config(mqtt_broker_ip, Sub_ai_Res, sub_topic_saveMSG)


        print(f'  - Mqtt Start')
        client.loop_forever()

    except Exception as e:
        rollgap_logging_instance.logMsg_Error("__main__  Error", e)