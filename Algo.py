import os
import sys
from io import BytesIO
import time
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import cv2
import numpy as np
from PIL import Image
import math
import base64
import threading
from datetime import datetime, timedelta
from lib.logging.logging import rollgap_logging
from lib.webSocket.websocket_server import rollgap_websocket
from lib.create_Folder.create_Folder import rollgap_creatFolder
from lib.config.config import rollgap_config
from lib.AlgoMethod.method import algorithm_method
from lib.Restart.restart_program import restart_program






rollgap_creatFolder_instance = rollgap_creatFolder()
algorithm_method_instance = algorithm_method()
rollgap_logging_instance = rollgap_logging()
rollgap_websocket_instance = rollgap_websocket()
rollgap_config_instance = rollgap_config()

saveOrder = "Off"




# # # #
# global image_window, image_window2
# image_window = pylon.PylonImageWindow()
# image_window.Create(1)
# image_window.SetImage(latest_image)
# image_window.Show()


##
def end_of_algo(image_rgb, camera_side, points_C_Roll, Roll_Gap_imageSavePath):
    
    try:
        start_time = time.time()

        # print(points_C_Roll)
        if testMode == 1 :
            #test
            DSimage_name = 'DS_t10.bmp'
            OSimage_name = 'OS_t1.bmp'
            # DSimage_name = 'DSt6.bmp'
            # OSimage_name = 'OSt7.bmp'
            DSimage_path = "./system_config/" + DSimage_name
            OSimage_path = "./system_config/" + OSimage_name
            if camera_side == "OS":
                image_rgb = cv2.imread(OSimage_path, cv2.IMREAD_COLOR)
            else:
                image_rgb = cv2.imread(DSimage_path, cv2.IMREAD_COLOR)
      

        
        if camera_side == "OS":
            borderTopBTM = OSborderTopBTM            
            points_list = points_C_Roll.tolist()
        else:
            borderTopBTM = DSborderTopBTM            
            points_list = points_C_Roll.tolist()

            

        # print(f"borderTopBTM=[{borderTopBTM}]")
        # borderTopBTM = 1080  # Top nozzle과 Bottom nozzle 간 구분
        # print(image_rgb)
        # print(camera_side)
        # print(borderTopBTM)
        # print(Threshold)
        # TOP1, TOP2, TOP3, BTM1, BTM2, BTM3 = algorithm_method.algorithmInterfaceEntry(image_rgb, camera_side, borderTopBTM, Threshold)

        TOP1, TOP2, TOP3, BTM1, BTM2, BTM3 = algorithm_method_instance.algorithmInterfaceEntry(image_rgb, camera_side, borderTopBTM, Threshold)


        # #
        # #### 1번
        # print(f"TOP1.x=[{TOP1.x}], TOP1.y=[{TOP1.y}]")
        # print(f"TOP2.x=[{TOP2.x}], TOP2.y=[{TOP2.y}]")
        # print(f"TOP3.x=[{TOP3.x}], TOP3.y=[{TOP3.y}]")
        # #
        # print(f"BTM1.x=[{BTM1.x}], BTM1.y=[{BTM1.y}]")
        # print(f"BTM2.x=[{BTM2.x}], BTM2.y=[{BTM2.y}]")
        # print(f"BTM3.x=[{BTM3.x}], BTM3.y=[{BTM3.y}]")



        #### 2번
        # example usage: distance between two points
        TOP1_TOP2_distanceBetweenPnts = f"{algorithm_method_instance.calculate_distance_between_points(TOP1, TOP2):.1f}"
        TOP2_TOP3_distanceBetweenPnts = f"{algorithm_method_instance.calculate_distance_between_points(TOP2, TOP3):.1f}"
        TOP3_BTM1_distanceBetweenPnts = f"{algorithm_method_instance.calculate_distance_between_points(TOP3, BTM1):.1f}"
        BTM1_BTM2_distanceBetweenPnts = f"{algorithm_method_instance.calculate_distance_between_points(BTM1, BTM2):.1f}"
        BTM2_BTM3_distanceBetweenPnts = f"{algorithm_method_instance.calculate_distance_between_points(BTM2, BTM3):.1f}"
       
        #### 3번
        #각 포인트 간의 중간 좌표
        T1_T2_Mid_point = algorithm_method_instance.findMidPoint( TOP1.x, TOP1.y, TOP2.x, TOP2.y ,0)
        T2_B2_Mid_point = algorithm_method_instance.findMidPoint( TOP2.x, TOP2.y, BTM2.x, BTM2.y, 1)
        T3_B1_Mid_point = algorithm_method_instance.findMidPoint( TOP3.x, TOP3.y, BTM1.x, BTM1.y, 2)
        B2_B3_Mid_point = algorithm_method_instance.findMidPoint( BTM2.x, BTM2.y, BTM3.x, BTM3.y, 3)
        
        
        # print(T3_B1_Mid_point.x, T3_B1_Mid_point.y)
        

        #### 4번
        # # # 수정 필요
        # # # Example usage: colating gap
        # segment1 = ((0, 0), (2, 0))  # Roll surface --> Find_C_Roll_Line.py로 찾기
        # segment2 = ((1, 1), (1, -1))  # Nozzle vertical segment
        # CoatingGapDistance = shortest_distance_between_segments(segment1, segment2)
        # # print("Coating Gap Distance: " + str(CoatingGapDistance))
        # if camera_side == "OS":
        #     # Example usage: colating gap
        #     segment1 = ((0, 0), (2, 0))  # Roll surface
        #     segment2 = ((1, 1), (1, -1))  # Nozzle vertical segment
        # else:
        #     segment1 = ((0, 0), (2, 0))  
        #     segment2 = ((1, 1), (1, -1)) 
        #     #
        # CoatingGapDistance = shortest_distance_between_segments(segment1, segment2)
        # # print("Coating Gap Distance: " + str(CoatingGapDistance))





        #### 5번
        # 
        # example usage: distance between single point and segment
        # point = (10, 10)
        # segment_start = (0, 0)
        # segment_end = (10, 0)
        # distance = distancePntSegment(segment_start, segment_end, point)
        # # print(f"distancePntSegment=[{distance}]")
        # #기존 코드
        # str1 = distancePntSegment(points_C_Roll[0], points_C_Roll[1], T1_T2_Mid_point)
        # str2 = distancePntSegment(points_C_Roll[2], points_C_Roll[3], T3_B1_Mid_point)
        # str3 = distancePntSegment(points_C_Roll[4], points_C_Roll[5], B2_B3_Mid_point)
        # print(f"str1={str1}, str2={str2} str3={str3}")
       

        # #변경 코드2
        # dis_SegtoP1 = distancePntSegment(points_C_Roll[0], points_C_Roll[1], (TOP1.x, TOP1.y))
        # dis_SegtoP2 = distancePntSegment(points_C_Roll[0], points_C_Roll[1], (TOP2.x, TOP2.y))
        # dis_SegtoP3 = distancePntSegment(points_C_Roll[2], points_C_Roll[3], T3_B1_Mid_point)
        # # dis_SegtoP3 = distancePntSegment((TOP2.x, TOP2.y), (BTM2.x, BTM2.y), T3_B1_Mid_point)
        # dis_SegtoP4 = distancePntSegment(points_C_Roll[4], points_C_Roll[5], (BTM2.x, BTM2.y))
        # dis_SegtoP5 = distancePntSegment(points_C_Roll[4], points_C_Roll[5], (BTM3.x, BTM3.y))

        #변경코드3
        point1 = algorithm_method_instance.find_intersection(points_C_Roll[0], points_C_Roll[1], TOP1.y)
        point2 = algorithm_method_instance.find_intersection(points_C_Roll[0], points_C_Roll[1], TOP2.y)
        # _point3 = find_intersection( (TOP2.x, TOP2.y), (BTM2.x, BTM2.y) , T3_B1_Mid_point.y)
        point3 = algorithm_method_instance.find_intersection( points_C_Roll[2], points_C_Roll[3] , T3_B1_Mid_point.y)
        point4 = algorithm_method_instance.find_intersection(points_C_Roll[4], points_C_Roll[5], BTM2.y)
        point5 = algorithm_method_instance.find_intersection(points_C_Roll[4], points_C_Roll[5], BTM3.y)
        # print(type(_point5))
        _point1 = algorithm_method_instance.tuple_to_point(point1)
        _point2 = algorithm_method_instance.tuple_to_point(point2)
        _point3 = algorithm_method_instance.tuple_to_point(point3)
        _point4 = algorithm_method_instance.tuple_to_point(point4)
        _point5 = algorithm_method_instance.tuple_to_point(point5)

        dis_SegtoP1 = f"{algorithm_method_instance.calculate_distance_between_points(_point1, TOP1):.1f}"
        dis_SegtoP2 = f"{algorithm_method_instance.calculate_distance_between_points(_point2, TOP2):.1f}"
        dis_SegtoP3 = f"{algorithm_method_instance.calculate_distance_between_points(_point3, T3_B1_Mid_point):.1f}"
        dis_SegtoP4 = f"{algorithm_method_instance.calculate_distance_between_points(_point4, BTM2):.1f}"
        dis_SegtoP5 = f"{algorithm_method_instance.calculate_distance_between_points(_point5, BTM3):.1f}"





        # # # #
        # # # # # # Wait for a key press and close the windows``
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y_%m_%d_%Hh_%Mm_%Ss")
        formatted_date = formatted_time[:10]
        formatted_time = formatted_time[11:]
        image_Save_path = f"{Roll_Gap_imageSavePath}/{camera_side}/{formatted_date}/{formatted_time}"
        data ={
            
            #확인
            "Camera_side": camera_side,
            # "borderTopBTM": borderTopBTM,
            "points_C_Roll": points_list, #list 형식
            #1번확인
            "TOP1": (TOP1.x, TOP1.y), #튜플형식
            "TOP2": (TOP2.x, TOP2.y),
            "TOP3": (TOP3.x, TOP3.y),
            "BTM1": (BTM1.x, BTM1.y),
            "BTM2": (BTM2.x, BTM2.y),
            "BTM3": (BTM3.x, BTM3.y),
            #2번 확인
            "Distance_P1_P2": TOP1_TOP2_distanceBetweenPnts, 
            "Distance_P2_P3": TOP2_TOP3_distanceBetweenPnts, 
            "Distance_P3_B1": TOP3_BTM1_distanceBetweenPnts, 
            "Distance_B1_B2": BTM1_BTM2_distanceBetweenPnts, 
            "Distance_B2_B3": BTM2_BTM3_distanceBetweenPnts,  
            #3번 확인
            "T1_T2_Mid":(T1_T2_Mid_point.x, T1_T2_Mid_point.y),
            "T3_B1_Mid":(T3_B1_Mid_point.x, T3_B1_Mid_point.y),
            "B2_B3_Mid":(B2_B3_Mid_point.x, B2_B3_Mid_point.y),                
            "T2_B2_Mid":(T2_B2_Mid_point.x, T2_B2_Mid_point.y),                
            # #4번 수정 필
            # "Coating_Gap_Distance":str(CoatingGapDistance),
            #5번 확인
            "dis_SegtoP1": dis_SegtoP1,
            "dis_SegtoP2": dis_SegtoP2,
            "dis_SegtoP3": dis_SegtoP3,
            "dis_SegtoP4": dis_SegtoP4,
            "dis_SegtoP5": dis_SegtoP5,

            "image_Save_path": image_Save_path,
        }
        #
      
       
       
        


        #color
        red_color = (0, 0, 255)
        yellow_color = (0, 255, 255)
        blue_color = (255, 0, 0)


        #좌표
        points = np.array([[TOP1.x, TOP1.y], [TOP2.x, TOP2.y], [TOP3.x, TOP3.y], [BTM1.x, BTM1.y], [BTM2.x, BTM2.y], [BTM3.x, BTM3.y]], np.int32)
        for point in points:
            cv2.circle(image_rgb, tuple(point), 15, red_color, -1)
        #롤선
        for i in range(0, len(points_C_Roll), 2):
            start_point = (points_C_Roll[i][0], points_C_Roll[i][1])
            end_point = (points_C_Roll[i + 1][0], points_C_Roll[i + 1][1])
            cv2.line(image_rgb, start_point, end_point, red_color, 10)
        # 좌표 간의 선을 그리기
        for i in range(len(points)-1):
            start_point = tuple(points[i])
            end_point = tuple(points[i+1])
            cv2.line(image_rgb, start_point, end_point, yellow_color, 10)

            
        # # #갭(# 세그먼트와 동일 Y 좌표에서 만나는 지점까지 선 그리기)
        # intersection_point1 = find_intersection(points_C_Roll[0], points_C_Roll[1], TOP1.y)
        # intersection_point2 = find_intersection(points_C_Roll[0], points_C_Roll[1], TOP2.y)
        # intersection_point3 = find_intersection(points_C_Roll[4], points_C_Roll[5], BTM2.y)
        # intersection_point4 = find_intersection(points_C_Roll[4], points_C_Roll[5], BTM3.y)
        # cv2.line(image_rgb,intersection_point1, [TOP1.x, TOP1.y] , blue_color, 10)
        # cv2.line(image_rgb,intersection_point2, [TOP2.x, TOP2.y] , blue_color, 10)
        # cv2.line(image_rgb,intersection_point3, [BTM2.x, BTM2.y] , blue_color, 10)
        # cv2.line(image_rgb,intersection_point4, [BTM3.x, BTM3.y] , blue_color, 10)

        # print(f"intersection_point1={intersection_point1}, type={type(intersection_point1)}")
        # print(f"_point1={_point1}, type={type(_point1)}")
        # print(f"_point1={point1}, type={type(point1)}")
        # print(f"T3_B1_Mid_point={T3_B1_Mid_point}, type={type(T3_B1_Mid_point)}")
        # print(f"_T3_B1_Mid_point={_T3_B1_Mid_point}, type={type(_T3_B1_Mid_point)}")
            

        # print(f"TOP1={TOP1}, type={type(TOP1)}")# TOP1=<__main__.Point2D object at 0x000002615047FED0>, type=<class '__main__.Point2D'>
        # print(f"point3={point3}, type={type(point3)}") # point3=(3340, 1063), type=<class 'tuple'>
        # print(f"T3_B1_Mid_point={T3_B1_Mid_point}, type={type(T3_B1_Mid_point)}")#T3_B1_Mid_point=<__main__.midPoint2D_ object at 0x0000026150747590>, type=<class '__main__.midPoint2D_'>
        # print(T3_B1_Mid_point.x, T3_B1_Mid_point.y)
      
        cv2.line(image_rgb, point1, tuple(TOP1), blue_color, 10)
        cv2.line(image_rgb, point2, tuple(TOP2), blue_color, 10)
        cv2.line(image_rgb, point3, (int(T3_B1_Mid_point.x), int(T3_B1_Mid_point.y)), blue_color, 10)
        cv2.line(image_rgb, point4, tuple(BTM2) , blue_color, 10)
        cv2.line(image_rgb, point5, tuple(BTM3), blue_color, 10)
        # # print(f"image_rgb={image_rgb}, type={type(image_rgb)}")
        # print(f"type={type(image_rgb)}")
        # #
        # #

   

        #웹 소켓용 이미지 변환
        latest_image = rollgap_websocket_instance.image_to_base64(image_rgb)
        # print(f"latest_image={latest_image}, type={type(latest_image)}")
        if latest_image is not None:
            if camera_side == "OS":
                image_data = {
                    "side": camera_side,
                    "image": latest_image
                }
            else:
                image_data = {
                    "side": camera_side,
                    "image": latest_image
                }
        else:
            pass

        


        #분석 데이터 전송
        dumpData = json.dumps(data)
        client.publish(PUB_TOPIC1, dumpData)

        #웹소켓 이미지 전송
        response_json = json.dumps(image_data)
        rollgap_websocket_instance.send_image(response_json)
        # print(f"Camera Side(Socket)={latest_image[0:2]}") //정상 송출




        #저장
        if saveOrder == "On":
            # print(f"Save Order - On!")
            #
            new_width = 960  # Maintain aspect ratio
            new_height = int(image_rgb.shape[0] * (new_width / image_rgb.shape[1]))
            resized_result = cv2.resize(image_rgb, (new_width, new_height))
            #
            # 
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.3
            font_thickness = 1
            y_position = 20 
            lineType = 2  
            #
            for key, value in data.items():
                text_to_display = f"{key}: {value}"
                cv2.putText(resized_result, text_to_display, (10, y_position), font, font_scale, red_color, font_thickness, lineType=lineType)
                y_position += 20 
            #
            #
            cv2.imwrite(f"{image_Save_path}.jpg", resized_result, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            #
            #
            # data ={
            #     # "points_C_Roll": points_list, #list 형식
            #     #
            #     "TOP1": f'POINT({TOP1.x}, {TOP1.x})',
            #     "TOP2": f'POINT({TOP2.x}, {TOP2.x})',
            #     "TOP3": f'POINT({TOP3.x}, {TOP3.x})',
            #     "BTM1": f'POINT({BTM1.x}, {BTM1.x})',
            #     "BTM2": f'POINT({BTM2.x}, {BTM2.x})',
            #     "BTM3": f'POINT({BTM3.x}, {BTM3.x})',         
            #     #
            #     "Distance_P1toP2": TOP1_TOP2_distanceBetweenPnts, 
            #     "Distance_P2toP3": TOP2_TOP3_distanceBetweenPnts, 
            #     "Distance_P3toP4": TOP3_BTM1_distanceBetweenPnts, 
            #     "Distance_P4toP5": BTM1_BTM2_distanceBetweenPnts, 
            #     "Distance_P5toP6": BTM2_BTM3_distanceBetweenPnts,  
            #     #            
            #     "T1_T2_Mid": f'POINT({T1_T2_Mid_point.x, T1_T2_Mid_point.y})',
            #     "T3_B1_Mid": f'POINT({T3_B1_Mid_point.x, T3_B1_Mid_point.y})',
            #     "B2_B3_Mid": f'POINT({B2_B3_Mid_point.x, B2_B3_Mid_point.y})',
            #     "T2_B2_Mid": f'POINT({T2_B2_Mid_point.x, T2_B2_Mid_point.y})',            
            #     #
            #     "dis_SegtoP1": dis_SegtoP1,
            #     "dis_SegtoP2": dis_SegtoP2,
            #     "dis_SegtoP3": dis_SegtoP3,
            #     "dis_SegtoP4": dis_SegtoP4,
            #     "dis_SegtoP5": dis_SegtoP5,

            #     "image_Save_path": image_Save_path,
            # }
            # points_dict={
            #     "p1": f'POINT({points_C_Roll[0][0], points_C_Roll[0][1]})',        
            #     "p2": f'POINT({points_C_Roll[1][0], points_C_Roll[1][1]})',        
            #     "p3": f'POINT({points_C_Roll[2][0], points_C_Roll[2][1]})',        
            #     "p4": f'POINT({points_C_Roll[3][0], points_C_Roll[3][1]})',        
            #     "p5": f'POINT({points_C_Roll[4][0], points_C_Roll[4][1]})',        
            #     "p6": f'POINT({points_C_Roll[5][0], points_C_Roll[5][1]})',        
            # }
            
            # if camera_side == "OS":
            #     mariadbHandler.insert("os_data", data)
            #     mariadbHandler.insert("os_c_roll_seg", points_dict)            
            # else:
            #     mariadbHandler.insert("ds_data", data)
            #     mariadbHandler.insert("ds_c_roll_seg", points_dict)

      
       
        # # #    
        work_time = time.time() - start_time
        print(f"side={camera_side},  Test Time = {round(work_time, 2)}")
        


    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)











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

def on_message(client, userdata, msg,  points_C_Roll_DS, points_C_Roll_OS):
    try:
        #
        #
        data = msg.payload
        topic = msg.topic
        #
        #
        if data is not None:
            # 
            if topic == SUB_TOPIC2:
                json_data = json.loads(data)
                # print(json_data)
                global saveOrder
                saveOrder = json_data["Save_Data"]
                if saveOrder == "On":
                    rollgap_creatFolder_instance.start_thread(Roll_Gap_imageSavePath)
                else:
                    rollgap_creatFolder_instance.stop_thread()

                data_to_publish = {
                    "Save_Data_return": saveOrder,
                }
                client.publish(PUB_TOPIC2, json.dumps(data_to_publish))

                
            elif topic == SUB_TOPIC1:

                json_data = json.loads(data)
                strSide = json_data["side"]
                strImage = json_data["image"]
                # print(f"strSide={strSide}, strImage={strImage[:2]}")

                decoded_data = base64.b64decode(strImage)
                #
                image = Image.open(BytesIO(decoded_data)).convert('RGB')
                # 
                numpy_array = np.array(image)
                # 
                maxvalue = numpy_array.max()
                # 
            # if maxvalue > pixelMax :         

                if strSide == "OS":
                    ###
                    end_of_algo(numpy_array, strSide, points_C_Roll_OS, Roll_Gap_imageSavePath)
                    
                elif strSide == "DS":                    
                    ##
                    end_of_algo(numpy_array, strSide , points_C_Roll_DS, Roll_Gap_imageSavePath)
            # else:
                # print(f"Balck Camera Image [{topic}]")
              
        else:
            print("Mqtt Data No!!!")

    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

def mqtt_Config(mqtt_broker_ip, pub_topic_ai_Res, sub_topic_cam, pub_topic_saveMSG, sub_topic_saveMSG,  points_C_Roll_DS, points_C_Roll_OS):
    try:
        global PUB_TOPIC1, PUB_TOPIC2, SUB_TOPIC1, SUB_TOPIC2, client
        MQTT_BROKER = mqtt_broker_ip
        PUB_TOPIC1 = pub_topic_ai_Res
        PUB_TOPIC2 = pub_topic_saveMSG
        SUB_TOPIC1 = sub_topic_cam
        SUB_TOPIC2 = sub_topic_saveMSG
        #
        print(f'  2. MQTT_BROKER = {MQTT_BROKER}')
        print(f'  3. PUB_TOPIC1 = {PUB_TOPIC1}')
        print(f'  4. PUB_TOPIC2 = {PUB_TOPIC2}')
        print(f'  6. SUB_TOPIC1 = {SUB_TOPIC1}')
        print(f'  7. SUB_TOPIC2 = {SUB_TOPIC2}')
        #
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        # client.on_message = on_message
        client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg,  points_C_Roll_DS, points_C_Roll_OS)
        client.connect(MQTT_BROKER, 1883, 60)
        
        #
        
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)

def config():
    try:
        #
        current_script_path = os.path.basename(__file__)
        current_script_name, _ = os.path.splitext(os.path.basename(current_script_path))
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
                # global testMode, Threshold, DSborderTopBTM, OSborderTopBTM, mariadbHandler, Roll_Gap_imageSavePath, pixelMax
                global testMode, Threshold, DSborderTopBTM, OSborderTopBTM, Roll_Gap_imageSavePath, pixelMax
                config = rollgap_config_instance.parse_json_config(config_file_path)
                #
                print('== Reading the config file... ==')
                #
                testMode = config["TestMode"]

                ##[Websocket_Config]
                websocketserver_ip = config["websocket_config"]["websocketserver_ip"]
                websocketserver_port = config["websocket_config"]["websocketserver_port"]

                #
                mqtt_broker_ip = config["Mqtt_Config"]["mqtt_broker_ip"]
                #
                pub_topic_ai_Res = config["Mqtt_Config"]["pub_topic_ai_Res"]
                #
                sub_topic_cam = config["Mqtt_Config"]["pub_topic_cam"]
                #
                pub_topic_saveMSG = config["Mqtt_Config"]["pub_topic_saveMSG"]
                sub_topic_saveMSG = config["Mqtt_Config"]["sub_topic_saveMSG"]
                #
                dump_path = config["path"]["dump_path"]
                algorithm_method_instance.receive_param(dump_path)
                #
                Roll_Gap_imageSavePath = config["path"]["Roll_Gap_imageSavePath"]
                DS_imageSavePath = config["path"]["DS_imageSavePath"]
                OS_imageSavePath = config["path"]["OS_imageSavePath"]
                rollgap_creatFolder_instance.create_folder(Roll_Gap_imageSavePath)
                rollgap_creatFolder_instance.create_folder(DS_imageSavePath)
                rollgap_creatFolder_instance.create_folder(OS_imageSavePath)
                #
                Threshold = config["Threshold"]["Algo_Threshold"]
                #
                DSborderTopBTM = config["borderTopBTM"]["DSborderTopBTM"]
                OSborderTopBTM = config["borderTopBTM"]["OSborderTopBTM"]
                #
                pixelMax = config["imagePixelMax"]["pixelMax"]
                #
                points_C_Roll_DS = np.array(config["C_Roll_configurations"]["DS"]["points_C_Roll"])
                points_C_Roll_OS = np.array(config["C_Roll_configurations"]["OS"]["points_C_Roll"])
                #
                # mariadbHandler = MariaDBHandler(config)
                #
                return config_file_path, websocketserver_ip, websocketserver_port, mqtt_broker_ip, pub_topic_ai_Res, sub_topic_cam,  pub_topic_saveMSG, sub_topic_saveMSG, points_C_Roll_DS, points_C_Roll_OS
        #
    except Exception as e:
        rollgap_logging_instance.logMsg_Error(f"[{sys._getframe().f_code.co_name}]", e)









if __name__=="__main__":

    try:
        #
        
        (config_file_path, websocketserver_ip, websocketserver_port, mqtt_broker_ip,
          pub_topic_ai_Res, sub_topic_cam,
          pub_topic_saveMSG, sub_topic_saveMSG,
            points_C_Roll_DS, points_C_Roll_OS) = config()
        #
        rollgap_websocket_instance.websocket_server(websocketserver_port, websocketserver_ip)
        #
        mqtt_Config(mqtt_broker_ip, pub_topic_ai_Res, sub_topic_cam, pub_topic_saveMSG, sub_topic_saveMSG, points_C_Roll_DS, points_C_Roll_OS)
        #
        config_watch_thread = threading.Thread(target=rollgap_config_instance.watch_config_changes, args=(config_file_path,), daemon=True)
        config_watch_thread.start()
        #
        #
        print(f'  - Mqtt Start')
        client.loop_forever()
        #
        restart_program()
        #        
    except Exception as e:
        rollgap_logging_instance.logMsg_Error("__main__  Error", e)




   