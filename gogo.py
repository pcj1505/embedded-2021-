

from typing import DefaultDict
from mcpi.minecraft import Minecraft
import mcpi.block as block
from gpiozero import Button
import pynput #pip install pynput
import time

mouse_drag = pynput.mouse.Controller()
mouse_button = pynput.mouse.Button

mc = Minecraft.create()


JOY_NORTH = 23
JOY_EAST = 17
JOY_SOUTH = 4
JOY_WEST = 25

BTN_bb=24

DELAY = 0.2

def mouse_move():
    joy_north = Button(JOY_NORTH)
    joy_east = Button(JOY_EAST)
    joy_south = Button(JOY_SOUTH)
    joy_west = Button(JOY_WEST)
    btn_bb=Button(BTN_bb)

    default = mouse_drag.position #현재 마우스 커서의 위치를 변수에 대입한다
    print(default)

    mx=default[0]
    my=default[1]

        # Don't check it's a safe position to move to - we test that later
        # Get current position and apply joystick movement
    position = mc.player.getTilePos()
    
    if (joy_north.is_pressed):
        my = my - 1
    if (joy_south.is_pressed):
        my = my + 1
    if (joy_east.is_pressed):  
        mx = mx + 1
    if (joy_west.is_pressed):
        mx = mx - 1
    if (btn_bb.is_pressed):
        print("kk")
        mx=0
        my=0

    #mouse_drag.position=(mx,my) #해당 좌표로 마우스커서 이동

    #time.sleep(DELAY)

    #mouse_drag.position=default #해당 좌표로 마우스커서 이동

	# mouse_drag.press(mouse_button.left) #마우스 왼쪽 버튼을 누른 상태로 유지한다
	# mouse_drag.release(mouse_button.left) #마우스 왼쪽 버튼을 뗀 상태로 유지한다

	# mouse_drag.press(mouse_button.right) #마우스 왼쪽 버튼을 누른 상태로 유지한다
	# mouse_drag.release(mouse_button.right) #마우스 왼쪽 버튼을 뗀 상태로 유지한다



#Run the main function when this program is run
if __name__ == "__main__":
    #mouse_drag.position=(0,0)
    #while True:
    #    mouse_move()
    print(mc.player.())


