# Pedometer-with-rp2040

rp2040을 이용한 걸음수 측정및  현재 상태(stop,run,walking)  gtts 음성으로 출력




블럭도
![서보모터](https://user-images.githubusercontent.com/103232943/175343649-bf2af77b-0e04-4a7a-9cc3-18b7df6713e9.PNG)


플로우 차트


![블럭도](https://user-images.githubusercontent.com/103232943/174290327-1d187a3c-f413-4fc3-b0fa-89d68b97d927.PNG)


rp2040내부의 센서는 

x축 =>  땅과 수평으로 걸어가는 방향의 변화

y축 =>  진행방향의 옆방향에서의 변화

z축 =>  수직으로 점프하는 방향으로의 변화를 나타낸다.

사람이 걸을때 평균적으로 x축 변화랑이 가장크고, 양옆으로 조금씩 왔다갔다 하는 변화가 곧 y축의 변화이고,z축이 위아래의 변화인데 
알고리즘으로 구현하려 했더니 약간의 문제가 있다. 
가속도 센서가 걸을때 정확하게 이동하는 방향으로 x축을 측정하는 센서가 향해 있어야 이게 성립한다.
센서를 주머니에 넣고 걸었는데 나는 x축으로 이동하지만 센서 입장에서는 y축으로 이동하는 결과가 될수 있다는것.

3축 가속도 센서중 가장큰 변화량을 가지는 값을 x축으로 삼고, 상대적으로 변화율이 적은 값을 y축, 나머지를 z축으로 삼으면 이를 해결할수있을것 같지만
사람에 따라 보폭도 다르고 위아래로 진동하는것과 양옆으로 이동하는것도 다 달라서 좀더 정확한 알고리즘의 필요성을 느끼고
한영환. (2015). 가속도 센서를 이용한 걸음수 검출 알고리즘.재활복지공학회 논문지 제9권 제3호 . 245-250.https://www.koreascience.or.kr/article/JAKO201515139872162.pdf
논문을 참고해서 걸음수 알고리즘을 작성해 보았다

![3축 가속도 센서](https://user-images.githubusercontent.com/103232943/171842388-c15a1357-d271-4917-84c1-f5800d6bff2a.PNG)

위의 논문에 따르면 3축 가속도에서 나온값으로 SVM이라는 신호벡터 크기를 구하고

![신호 벡터 크기값](https://user-images.githubusercontent.com/103232943/171842590-84b360c8-582c-4f5c-910d-df0959be35f3.PNG)

그래프로 나타내면 x,y,z 축의 가속도 정보가 아래 SVM신호 벡터 크기 정보처럼 나온다고 한다.


이 SVM 신호를 가지고 2개의 임계값을 고정으로 설정하는게 아닌 걸음에 따라 다르게 임계값을 설정하여
걸음수의 정확성을 높였다고 하는데 이건 다음에 기회가 되면 만들어보고 우선 고정으로 임계값을 2개 설정하여 걸음수를 구하는 알고리즘을
작성해 보려고 한다.

![임계값](https://user-images.githubusercontent.com/103232943/171843793-6c8155eb-aa41-4a14-9d81-6b012197d51c.PNG)

임계값을 C1,C2이렇게 2개를 잡고 C1을 넘고 한번 C2아래로 내려갔다가 오면 1걸음을 걸었다고 판단하고 10초동안 재었을때 걸음수가 많으면 뛰는 상태라고 생각하고 코드를 짜보았다.

1.  rp2040 내부의 센서를 이용해서 3축정보를 받아오고 이를가공하여 평균 걸음수를 구하고
    I2c  통신 프로토콜을 이용해 외부 rp2040장치 => 라즈베리파이 내부로 'rp2040' Topic 으로 Text형식의 데이터를 전송한다.

---
waling_test.py
```
import network,time
from umqtt.simple import MQTTClient #导入MQTT板块
from machine import I2C,Pin,Timer
from lsm6dsox import LSM6DSOX

step1 = 0
from machine import Pin, I2C
lsm = LSM6DSOX(I2C(0, scl=Pin(13), sda=Pin(12)))


count=0
SVM_SUM=0
C1=0
C2=0
walking=0
pub_status=''
avr_walk=0
def WIFI_Connect():
    wlan = network.WLAN(network.STA_IF) #STA模式
    wlan.active(True)                   #激活接口
    start_time=time.time()              #记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('iptime105', '@rjsghks12') #输入WIFI账号密码
        
    if wlan.isconnected():
        print('network information:', wlan.ifconfig())
        return True
    
def MQTT_Send(tim):
    client.publish(TOPIC, str(avr_walk)+pub_status)
    print(str(avr_walk)+'steps per second '+pub_status)

while (True):
    msg='Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*lsm.read_accel())
    list=(msg.split())
    x=float(list[2])
    y=float(list[4])
    z=float(list[6])
    SVM=x+y+z
    if SVM> 2.5:
        C1=1
    elif SVM<0.9:
        C2=1
    if C1==1 and C2==1:
        C1=0
        C2=0
        walking+=1
    
    count+=1
    
    print('걸음수'+str(walking))

    if count== 100:
        avr_walk=walking/10
        print('1초동안 평균 걸음수'+str(avr_walk))
        if avr_walk>3:
            pub_status='he is running'
            print(pub_status)
        elif avr_walk>1:
            pub_status='he is walking'
            print(pub_status)
        elif avr_walk<1:
            pub_status='he is standing'
            print(pub_status)
        walking=0
        count=0
        break
    time.sleep_ms(100)

if WIFI_Connect():
    SERVER = '192.168.0.6'   # my rapa ip address , mqtt broker가 실행되고 있음
    PORT = 1883
    CLIENT_ID = '' # clinet id 이름
    TOPIC = 'rp2040' # TOPIC 이름
    client = MQTTClient(CLIENT_ID, SERVER, PORT,keepalive=30)
    client.connect()

    #开启RTOS定时器，编号为-1,周期1000ms，执行socket通信接收任务
    tim = Timer(-1)
    tim.init(period=1000, mode=Timer.PERIODIC,callback=MQTT_Send)
```


결과창을 보면 10초동안의 걸음수를 측정하고 평균을 내어
1초에 평균 몇걸음을 걸었는지 알려준다.
이 걸음수로 현재 상태가 걷는 상태인지 서있는 상태인지 달리는 상태인지 판단하여 알려주고
현재상태와 평균 걸음수를  'rp2040'Topic으로 날려준다.

![결과창](https://user-images.githubusercontent.com/103232943/174136130-8e343ac0-5ece-4442-939b-d30fc77d0ffe.PNG)


2.'rp2040' Topic으로 날아간 text를 라즈베리파이로 받아와서
서브모터 속도제어 & Gtts 음성출력 
```
import speech_recognition as sr
from gtts import gTTS
import playsound
import random
from typing import List
from pymata4 import pymata4
import time
import pygame
import paho.mqtt.client as mqtt_client

pygame.mixer.init()
board = pymata4.Pymata4()
servo=board.set_pin_mode_servo(11) 

broker_address = "localhost"
broker_port = 1883

topic = "rp2040"

def speak(text):
    tts=gTTS(lang='ko',text=text)
    filename='/home/pi/Desktop/1801298/voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)
def speak2(text):
    tts=gTTS(lang='ko',text=text)
    filename='/home/pi/Desktop/1801298/voice2.mp3'
    tts.save(filename)
    playsound.playsound(filename)
def speak3(text):
    tts=gTTS(lang='ko',text=text)
    filename='/home/pi/Desktop/1801298/voice3.mp3'
    tts.save(filename)
    playsound.playsound(filename)
def speaker_out():
    pygame.mixer.music.load("//home/pi/Desktop/1801298/voice.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
def speaker_out2():
    pygame.mixer.music.load("//home/pi/Desktop/1801298/voice2.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
def speaker_out3():
    pygame.mixer.music.load("//home/pi/Desktop/1801298/voice3.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


speak('he is standing')
speak2('he is walking')
speak3('he is running')

def move_servo(d):
    i=0
    while(1):
        board.servo_write(11,i)
        i+=1
        if i==181:
            board.servo_write(11,0)
            break
        time.sleep(d)

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
        else:
            print(f"Failed to connect, Returned code: {rc}")

    def on_disconnect(client, userdata, flags, rc=0):
        print(f"disconnected result code {str(rc)}")

    def on_log(client, userdata, level, buf):
        print(f"log: {buf}")

    # client 생성
    client_id = f"mqtt_client_{random.randint(0, 1000)}"
    client = mqtt_client.Client(client_id)

    # 콜백 함수 설정
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log

    # broker 연결
    client.connect(host=broker_address, port=broker_port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if "standing" in msg.payload.decode():
            speaker_out()
            move_servo(0.05)
        elif "walking" in msg.payload.decode():
            speaker_out2()
            move_servo(0.01)
        elif "running" in msg.payload.decode():
            speaker_out3()
            move_servo(0.005)
        
    
    client.subscribe(topic) #1
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
```    

3. 'rp2040' Topic 으로 날아간 Text를 노드레드 대시보드로 확인하기


![프랩 대시보드](https://user-images.githubusercontent.com/103232943/174229119-24b59401-aee6-46db-a882-da7052ec1071.PNG)


4. 동작 영상 확인

<iframe width="994" height="559" src="https://www.youtube.com/embed/37BgV_y6UZ8" title="소프트웨어학부 스마트모빌리티전공 과제 mqtt_gtts_sevo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>






https://user-images.githubusercontent.com/103232943/174260662-2aab5a2f-9a70-4301-b295-c55b33c6a9d4.mp4



1:04초 오타 서있는 상태와 뛰는 상태의 서브모터 속도 차이
