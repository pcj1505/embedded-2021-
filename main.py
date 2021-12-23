import mcpi.minecraft as minecraft
import mcpi.block as block
from mcpi.minecraft import Minecraft
import RPi.GPIO as GPIO
import time
import cvlib as cv
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from gpiozero import LED

#model setting
model = load_model('CNN_model.h5')
print("success")

#mcsetting
mc=Minecraft.create()

flat_size_x=30
flat_size_y=20
flat_size_z=50
flat_position=minecraft.Vec3(0,0,0)


LED_PIN=5
led1=LED(LED_PIN)
LED_PIN2=6
led2=LED(LED_PIN2)

#music setting
buzzer = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setwarnings(False)

pwm = GPIO.PWM(buzzer, 1.0)

scale = [262, 294, 330, 349, 392, 440, 494, 523]

DELAY=0.1

JOY_NORTH = 23 #left
JOY_EAST = 17 #up
JOY_SOUTH = 4 #right
JOY_WEST = 25 #down

BTN8 = 16
BTN7 = 20
BTN6 = 21
BTN5 = 26

dnum=-1

GPIO.setup(JOY_NORTH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOY_EAST, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOY_SOUTH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOY_WEST, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(BTN8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3,400)
    cap.set(4,300)
    count=0
    recog_num=0
    auto_jump=False
    btn_num8=0
    btn_num6=0
    btn_num5=0
    dnum=-1
    knum=-1
    #공연장구현
    #go_flat()
    #공연장에 음악타일깔기
    #set_music()
    
    #사용자를 문앞에 위치시킴
    #set_front_door()
    #frontmusic
    #set_front_music()
    #문열기
    #open_door()
    #sleep 10 sec
    #time.sleep(10)
    #문닫기
    #close_door()

    while(True):
        if dnum==0:
            close_door()
            dnum=dnum-1
        elif dnum>0:
            dnum=dnum-1
        else:
            dnum=-1

            mx, my, mz=mc.player.getPos()
            #mc.postToChat(mx)
            if (mx>-5 and mx<=-1 and my==2 and mz>flat_size_z/2-1 and mz<flat_size_z/2+2):
                if recog_num==0:
                    mc.postToChat("recog_mask_ing")
                frame, recog_num=mask_recog(cap, recog_num)
                
                cv2.imshow('frame', frame)
                mc.postToChat(recog_num)
                # 0입력시 종료.
                #if cv2.waitKey(1) == ord('0'):
                #    break
                cc=cv2.waitKey(1)
                if recog_num==10:
                    cc=27
                if cc==27:
                    recog_num=0
                    cv2.destroyAllWindows()
                    dnum = open_door()
                    #time.sleep(10)
                    #close_door()

            else: #playmusic
                led1.on()
                cv2.destroyAllWindows()
                recog_num=0
                mx, my, mz=mc.player.getPos()
                bnum=mc.getBlock(mx,my-1,mz)
                if knum==5:
                    play(bnum)

        #mc.postToChat(dnum)

        if (GPIO.input(BTN7) == False):
            if(auto_jump==True):
                auto_jump = False
                mc.postToChat("Auto jump disabled")
        if (GPIO.input(BTN8) == False):   # pressed
            #mc.postToChat("123")
            btn_num8=1
        else:
            btn_num8=0
         
        if (GPIO.input(BTN6) == False):
            btn_num6=1
        else:
            btn_num6=0

        if (GPIO.input(BTN5)==False):
            btn_num5=1
        else:
            btn_num5=0

        if (btn_num8 == 1):
            #mc.postToChat("8button")
            mc.postToChat("make theater")
            knum=5
            set_front_door()
            go_flat() #젤 오른쪽 밑버튼
            set_music()
        if (btn_num5 == 1):
            mc.postToChat("set start position")
            #mc.postToChat("5button")
            set_front_door()  #오른쪽 세번째 윗버튼
        if (btn_num6 == 1):
            mc.postToChat("set music position")
            #mc.postToChat("6button")
            set_front_music() #오른쪽 세번째 밑버튼


        position = mc.player.getTilePos()
        if (GPIO.input(JOY_SOUTH) == False):
            position.z = position.z + 1
        if (GPIO.input(JOY_EAST) == False):
            position.x = position.x + 1
        if (GPIO.input(JOY_WEST) == False):
            position.x = position.x - 1
        if (GPIO.input(JOY_NORTH) == False):
            position.z = position.z - 1
            block_id = mc.getBlock(position)
        mc.player.setTilePos(position)
        time.sleep(DELAY)
        
        
            

    cap.release()




def mask_recog(cap, recog_num):
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1) # 좌우 대칭
    if(ret) :
        face_locations, confidence = cv.detect_face(frame)
        for (left, top, right, bottom) in face_locations:
            face_image = frame[top+49:bottom-3, left:right-3]
            try:
                face_image1=cv2.resize(face_image, (64,64),interpolation=cv2.INTER_AREA)
            except:
                pass
                        
            x = img_to_array(face_image1)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
                        
            prediction = model.predict(x)
                        
            if prediction < 0.5: # 마스크 미착용으로 판별되면, 
                cv2.rectangle(frame, (left,top), (right,bottom), (0,0,255), 2)
                Y = top - 10 if top - 10 > 10 else top + 10
                text = "No Mask ({:.2f}%)".format((1 - prediction[0][0])*100)
                cv2.putText(frame, text, (left,Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                led1.on()
                led2.off()
                            
            else: # 마스크 착용으로 판별되면
                cv2.rectangle(frame, (left,top), (right,bottom), (0,255,0), 2)
                Y = top - 10 if top - 10 > 10 else top + 10
                text = "Mask ({:.2f}%)".format(prediction[0][0]*100)
                cv2.putText(frame, text, (left,Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                recog_num+=1
                led1.off()
                led2.on()

    return frame, recog_num
    
def set_front_door():
    fx=0
    fy=1
    fz=flat_size_z/2
    
    mc.player.setPos(fx-10,3,fz)

def set_front_music():
    fx=25
    fy=5
    fz=1.4
    
    mc.player.setPos(fx,fy,fz)

def open_door():
    mc.postToChat("open the door")
    #open door
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y+2, \
        flat_position.z+flat_size_z/2-1, \
        flat_position.x, \
        flat_position.y+5, \
        flat_position.z+flat_size_z/2+1, \
        block.AIR.id)
    led2.off()

    return 50

def close_door():
    mc.postToChat("close the door")
    #close door
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y+2, \
        flat_position.z+flat_size_z/2-1, \
        flat_position.x, \
        flat_position.y+5, \
        flat_position.z+flat_size_z/2+1, \
        block.WOOD.id)
      

def go_flat():
    #공연장 내부 공간 생성
    mc.setBlocks(   \
        flat_position.x-10, \
        flat_position.y, \
        flat_position.z-10, \
        flat_position.x + flat_size_x+10, \
        flat_position.y+flat_size_y+10, \
        flat_position.z+flat_size_z+30, \
        block.AIR.id)

    #공연장 바닥 평탄화
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y, \
        flat_position.z-1, \
        flat_position.x + flat_size_x, \
        flat_position.y+1, \
        flat_position.z+flat_size_z+15, \
        98)

    #공연장 주변 공간 생성
    mc.setBlocks(   \
        flat_position.x-1, \
        flat_position.y, \
        flat_position.z-1, \
        flat_position.x-15, \
        flat_position.y+10, \
        flat_position.z+flat_size_z+15, \
        block.AIR.id)

    #공연장 주변 바닥 평탄화
    mc.setBlocks(   \
        flat_position.x-1, \
        flat_position.y, \
        flat_position.z-1, \
        flat_position.x-15, \
        flat_position.y+1, \
        flat_position.z+flat_size_z+20, \
        block.GRASS.id)
    mc.setBlocks(   \
        flat_position.x-10, \
        flat_position.y, \
        flat_position.z-10, \
        flat_position.x + flat_size_x+10, \
        flat_position.y, \
        flat_position.z+flat_size_z+10, \
        block.GRASS.id)

    #공연장 벽 생성
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y, \
        flat_position.z-1, \
        flat_position.x, \
        flat_position.y+flat_size_y, \
        flat_position.z+flat_size_z+15, \
        98)
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y, \
        flat_position.z-1, \
        flat_position.x+flat_size_x, \
        flat_position.y+flat_size_y, \
        flat_position.z-1, \
        98)
    mc.setBlocks(   \
        flat_position.x+flat_size_x, \
        flat_position.y, \
        flat_position.z-1, \
        flat_position.x+flat_size_x, \
        flat_position.y+flat_size_y, \
        flat_position.z+flat_size_z+15,\
        98)
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y, \
        flat_position.z+flat_size_z+15, \
        flat_position.x+flat_size_x, \
        flat_position.y+flat_size_y, \
        flat_position.z+flat_size_z+15, \
        98)

    #공연장 문 구현
    mc.setBlocks(   \
        flat_position.x, \
        flat_position.y, \
        flat_position.z+flat_size_z/2-1, \
        flat_position.x, \
        flat_position.y+5, \
        flat_position.z+flat_size_z/2+1, \
        block.WOOD.id)
    
    #무대 바닥 생성
    mc.setBlocks(   \
        flat_position.x+20, \
        flat_position.y+1, \
        flat_position.z, \
        flat_position.x+29, \
        flat_position.y+2, \
        flat_position.z+69, \
        block.STAIRS_NETHER_BRICK.id)

    #무대 계단 생성1
    mc.setBlocks(   \
        flat_position.x+19, \
        flat_position.y+2, \
        flat_position.z, \
        flat_position.x+19, \
        flat_position.y+2, \
        flat_position.z, \
        block.STAIRS_NETHER_BRICK.id)

    #무대 계단 생성2
    mc.setBlocks(   \
        flat_position.x+19, \
        flat_position.y+2, \
        flat_position.z+49, \
        flat_position.x+19, \
        flat_position.y+2, \
        flat_position.z+49, \
        block.STAIRS_NETHER_BRICK.id)

    #무대 계단 생성3
    mc.setBlocks(   \
        flat_position.x+19, \
        flat_position.y+2, \
        flat_position.z+25, \
        flat_position.x+19, \
        flat_position.y+2, \
        flat_position.z+25, \
        block.STAIRS_NETHER_BRICK.id)
        

    #mask_recog_block
    mc.setBlocks(   \
        flat_position.x-1, \
        flat_position.y+1, \
        flat_position.z+flat_size_z/2-1, \
        flat_position.x-5, \
        flat_position.y+1, \
        flat_position.z+flat_size_z/2+1, \
        block.BRICK_BLOCK.id)
    
def set_music():    
    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+1+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+4+1, \
        #block.WOOL.id,14)
        15) 

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+5+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+8+1, \
        #block.WOOL.id,14)
        16)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+9+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+12+1, \
        #block.WOOL.id,14)
        15)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+13+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+16+1, \
        #block.WOOL.id,14)
        13)
    
    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+17+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+20+1, \
        #block.WOOL.id,14)
        15)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+21+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+24+1, \
        #block.WOOL.id,14)
        13)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+25+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+30+1, \
        #block.WOOL.id,14)
        12)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+33+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+36+1, \
        #block.WOOL.id,14)
        15)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+37+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+40+1, \
        #block.WOOL.id,14)
        16)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+41+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+44+1, \
        #block.WOOL.id,14)
        15)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+45+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+48+1, \
        #block.WOOL.id,14)
        13)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+49+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+50+1, \
        #block.WOOL.id,14)
        15)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+51+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+52+1, \
        #block.WOOL.id,14)
        13)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+53+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+54+1, \
        #block.WOOL.id,14)
        12)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+55+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+56+1, \
        #block.WOOL.id,14)
        13)

    mc.setBlocks(
        flat_position.x+24, \
        flat_position.y+1, \
        flat_position.z+57+1, \
        flat_position.x+25, \
        flat_position.y+2, \
        flat_position.z+60+1, \
        #block.WOOL.id,14)
        1)

def play(bnum):
    if (bnum==1):
        pwm.ChangeFrequency(scale[0])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==12):
        pwm.ChangeFrequency(scale[1])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==13):
        pwm.ChangeFrequency(scale[2])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==14):
        pwm.ChangeFrequency(scale[3])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==15):
        pwm.ChangeFrequency(scale[4])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==16):
        pwm.ChangeFrequency(scale[5])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==17):
        pwm.ChangeFrequency(scale[6])   
        pwm.start(10)
        time.sleep(0.1)
    elif (bnum==18):
        pwm.ChangeFrequency(scale[7])   
        pwm.start(10)
        time.sleep(0.1)
    else:
        pwm.stop()

if __name__=="__main__":
    main()
    