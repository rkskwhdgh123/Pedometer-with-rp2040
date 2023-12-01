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