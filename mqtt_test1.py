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