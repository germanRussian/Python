import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
import serial
import time
import datetime
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import serial.tools.list_ports
import threading

from lib.logging.logging import rollgap_logging
from lib.config.config import rollgap_config




rollgap_logging_instance = rollgap_logging()
rollgap_config_instance = rollgap_config()









#
def find_serial_ports():
    try:
        available_ports = list(serial.tools.list_ports.comports())
        if not available_ports:
            client.publish(PUB_TOPIC, "Error-12")
            rollgap_logging_instance.logMsg("No serial ports are available.")
        else:   
            for port_info in available_ports:
                    # print(f"포트 이름: {port_info.device}, 설명: {port_info.description}")
                    if port_info.description[0:12] == "Prolific USB":
                        global selectedPort
                        selectedPort = str(port_info.device)
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("find_serial_ports_Error", e)

#
def LEDPortSet():
    try:
        #
        global LEDPort
        LEDPort = serial.Serial(
            port = selectedPort, 
            baudrate=19200, 
            parity='N',
            stopbits=1,
            bytesize=8
        )
        LEDPort.isOpen()
        #
        if(LEDPort.is_open):
            print(f"  4. Selected Port: {LEDPort.name } Open")
            print(f"  5. Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        #
    except Exception as e:
        client.publish(PUB_TOPIC, f"Error-13")
        rollgap_logging_instance.logMsg_Error("LEDPortSet_Error", e)

#
def monitor_serial_ports(interval):
    try:
        while True:
            find_serial_ports()
            time.sleep(interval)
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("monitor_serial_ports_Error", e)
        
#1ch val=set 2ch val=set
def led_allCh_setValue(value1ch, value2ch):
    try:
      if(LEDPort.is_open):
        #
        value1ch_re = int(value1ch)
        value2ch_re = int(value2ch)
        #
        if value1ch_re <= 0:
            value1ch_re = 0
        if value2ch_re <= 0:
            value2ch_re = 0
        if value1ch_re > 999:
            value1ch_re = 999
        if value2ch_re > 999:
            value2ch_re = 999
        #
        hexvalue1 = format(value1ch_re,'x').zfill(4)
        hexvalue2 = format(value2ch_re,'x').zfill(4)
        b1 = bytes([int(hexvalue1[0:2], 16)])
        b2 = bytes([int(hexvalue1[2:4], 16)])
        b3 = bytes([int(hexvalue2[0:2], 16)])
        b4 = bytes([int(hexvalue2[2:4], 16)])
        #
        #1ch선택
        msg1 = b'\x01\x00\x01\x20\x01\x04' 
        msg1.hex()
        LEDPort.write(msg1)
        LEDPort.flush()
        #
        # #1ch 값 변경
        msg1_1 = bytearray(b'\x01\x00\x02\x28')
        msg1_1.extend(b2)
        msg1_1.extend(b1)
        msg1_1.append(4)
        msg1_1.hex()
        LEDPort.write(msg1_1)
        LEDPort.flush()
        #
        #2ch선택
        msg2 = b'\x01\x00\x01\x20\x02\x04' 
        msg2.hex()
        LEDPort.write(msg2)
        LEDPort.flush()
        #
        #2ch 값 변경
        msg2_1 = bytearray(b'\x01\x00\x02\x28')
        msg2_1.extend(b4)
        msg2_1.extend(b3)
        msg2_1.append(4)
        msg2_1.hex()
        LEDPort.write(msg2_1)
        LEDPort.flush()
        #
    except Exception as e:
        LEDPortSet()
        rollgap_logging_instance.logMsg_Error("led_allCh_setValue_Error", e)

#모든 채널 온오프 제어
def led_onoff(onoffValue, value_1ch, value_2ch):
    try:
        #
        if(LEDPort.is_open):
            #ch onoff 변경
            msg = bytearray(b'\x01\x00\x01\x34')
            msg.append(onoffValue)
            msg.append(4)
            msg.hex()
            LEDPort.write(msg)
            LEDPort.flush()
            led_allCh_setValue(value_1ch, value_2ch)
            #
    except Exception as e:
        LEDPortSet()
        rollgap_logging_instance.logMsg_Error("led_onof_Error", e)

#LED 모든 상태 확인 - 원하는 값 파싱
def led_Check(led_job):
    try:       
        #
        msg1 = b'\x01\x00\x01\x2C\x04\x04' # 전체 상태값 요청 패킷
        msg1.hex()
        LEDPort.write(msg1)
        LEDPort.flush()
        #
        time.sleep(.3)
        led_state = LEDPort.read_all().decode('utf-8')
        #
        if led_state is not None :
            strings = led_state.split()
            #
            led1_ = strings[47]
            led1_re = led1_[6:8]
            #
            led2_ = strings[48]
            led2_re = led2_[6:8]
            #
            led1_value = strings[42]
            led1_value_re = led1_value[6:9].replace(",", "")
            #
            led2_value = strings[43]
            led2_value_re = led2_value[6:9]
            #
            client.publish(PUB_TOPIC, json.dumps({
                "led1_":led1_re,  #ON
                "led2_":led2_re,  #ON
                "led1_value": led1_value_re,  #249
                "led2_value": led2_value_re,  #249
                "led_job": led_job,
            }))

    except Exception as e:
        LEDPortSet()
        client.publish(PUB_TOPIC, f"Error-14")
        rollgap_logging_instance.logMsg_Error("led_Check_Error", e)

# LED welcomLight
def welcomLight():
    try:
        print('\n== WelcomLight!! ==')
        #
        # for i in range(3):
        #     led_onoff(0,0,0)
        #     time.sleep(.5)
        #     led_onoff(3,999,999)
        #     time.sleep(.5)
        # #
        # for j in range(3):
        #     led_allCh_setValue(14, 999)
        #     time.sleep(.5)
        #     led_allCh_setValue(999, 14)
        #     time.sleep(.5)
        #
        for abc in reversed(range(255)):
            led_allCh_setValue(abc, abc)
        #
        led_allCh_setValue(999, 999)
        time.sleep(.5) 
        #
        led_allCh_setValue(0, 0)
        time.sleep(.5) 
        #
        led_allCh_setValue(999, 999)
        time.sleep(.5) 
        #
        led_allCh_setValue(0, 0)
        time.sleep(1)
        #
        print('\n== LED Program Ready & Start!!! ==')
        #
    except Exception as e:
        LEDPortSet()
        rollgap_logging_instance.logMsg_Error("welcomLight_Error", e)

#구독
def on_connect(client, userdata, flags, rc):
    try:
        client.subscribe(SUB_TOPIC,  0)        
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("on_connect_Error", e)

# subscriber callback
def on_message(client, userdata, msg):
    try:
        if msg is not None:
            data = json.loads(msg.payload)
            #
            global led1_intensity, led2_intensity,  led_job
            led1_intensity = data["led1_intensity"]
            led2_intensity = data["led2_intensity"]
            # print(f'led1_intensity={led1_intensity}, led2_intensity={led2_intensity}')
            led_job = str(data["led_job"])
            # print(data)
            #
            # if led_job == "1":
            #     led_allCh_setValue(led1_intensity, led2_intensity)
            #     led_Check()

            # if led_job == "2":
            #     led_allCh_setValue(led1_intensity, led2_intensity)
            #     led_Check()

            led_allCh_setValue(led1_intensity, led2_intensity)
            led_Check(led_job)
            #
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("on_message_Error", e)

#
def mqtt_Config(mqtt_broker_ip, pub_topic_name, sub_topic_name):
    try:
        global MQTT_BROKER, PUB_TOPIC, SUB_TOPIC, client
        MQTT_BROKER = mqtt_broker_ip
        PUB_TOPIC = pub_topic_name
        SUB_TOPIC = sub_topic_name
        print(f'  1. MQTT_BROKER = {MQTT_BROKER}')
        print(f'  2. PUB_TOPIC = {PUB_TOPIC}')        
        print(f'  3. SUB_TOPIC = {SUB_TOPIC}')

        #mqtt
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, 1883, 60)
        
        
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("on_message_Error", e)

#
def config():
    try:
        #
        current_script_path = os.path.basename(__file__)
        current_script_name, _ = os.path.splitext(os.path.basename(current_script_path))
        # print(f"== The current script file name ==\n  -{current_script_path}\n")
        #       
        rollgap_logging_instance.logFileCreate(current_script_name)
        #
        config_folder_path = "./system_config"
        config_file_path = f'{config_folder_path}/rollgap_config.json'
        # 
        if not os.path.exists(config_folder_path):
            os.makedirs(config_folder_path)
            rollgap_config_instance.rollgap_config_create(config_file_path)
        else :
            if not os.path.isfile(config_file_path):
                rollgap_config_instance.rollgap_config_create(config_file_path)
            else:

                
                config = rollgap_config_instance.parse_json_config(config_file_path)
                #
                print('== Reading the config file... ==')
                #
                mqtt_broker_ip = config["Mqtt_Config"]["mqtt_broker_ip"]
                pub_topic_name = config["Mqtt_Config"]["pub_topic_LED"]
                sub_topic_name = config["Mqtt_Config"]["sub_topic_LED"]
                #
                return mqtt_broker_ip, pub_topic_name, sub_topic_name
            

    except Exception as e:
        rollgap_logging_instance.logMsg_Error("config_Error", e)

#
if __name__=="__main__":
    try:
        mqtt_broker_ip, pub_topic_name, sub_topic_name = config()
        #
        mqtt_Config(mqtt_broker_ip, pub_topic_name, sub_topic_name)
        #
        find_serial_ports()
        #
        LEDPortSet()
        #
        welcomLight()
        #
        #
        # 데몬 스레드로 serial port 확인 스레드 실행
        monitor_thread = threading.Thread(target=monitor_serial_ports, args=(10,), daemon=True)
        monitor_thread.start()
        #
        #
        client.loop_forever(retry_first_connection=True)
        #
        #
        client.loop_stop()
        #
    except Exception as e:
        #
        client.publish(PUB_TOPIC, json.dumps({
                "led1_":"OF",  
                "led2_":"OF",  
                "led1_value": 0,  
                "led2_value": 0,  
        }))
        rollgap_logging_instance.logMsg_Error("__main__.", f"Exit_the_program.={e}")
        
        







