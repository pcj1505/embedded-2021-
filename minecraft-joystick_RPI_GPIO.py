# Move around in Minecraft using a joystick
from mcpi.minecraft import Minecraft
import mcpi.block as block
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
JOY_NORTH = 23
JOY_EAST = 17
JOY_SOUTH = 4
JOY_WEST = 25

BTN8 = 16
BTN7 = 20
BTN6 = 21
BTN5 = 26

GPIO.setup(JOY_NORTH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOY_EAST, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOY_SOUTH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(JOY_WEST, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(BTN8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#from gpiozero import Button
import time

# Setup various buttons and connect to minecraft
mc = Minecraft.create()


# Time to wait before moves
DELAY = 0.2

# Main loop to monitor buttons
def main():   
    # Autojump setting
    auto_jump = False
    
    
    while True:
        # jump status can be 0 = no jump, 1 = jump now, 2 = autojump, 3 = long_jump 
        jump = 0
        # check for each button and set appropriate status
        if (GPIO.input(BTN_JMP) == False) :   # pressed
            jump = 1
        # toggle auto jump status
        if (GPIO.input(BTN_AUTOJMP) == False) :
            if (auto_jump == True):
                auto_jump = False
                mc.postToChat("Auto jump disabled")
            else :
                auto_jump = True
                mc.postToChat("Auto jump enabled")
        if (auto_jump == True):
            jump = 2
        if (GPIO.input(BTN_LGEJMP) == False):
            jump = 3
        
        # Don't check it's a safe position to move to - we test that later
        # Get current position and apply joystick movement
        position = mc.player.getTilePos()
        if (GPIO.input(JOY_NORTH) == False):
            position.z = position.z - 1
            mc.postToChat("UP Key : Pressed")
        if (GPIO.input(JOY_SOUTH) == False):
            position.z = position.z + 1
            mc.postToChat("DOWN Key : Pressed")
        if (GPIO.input(JOY_EAST) == False):
            position.x = position.x + 1
            mc.postToChat("RIGHT Key : Pressed")
        if (GPIO.input(JOY_WEST) == False):
            position.x = position.x - 1
            mc.postToChat("LEFT Key : Pressed")

        if (jump == 2): 
            # Jump only if next position is solid
            block_id = mc.getBlock(position)
            if (block_id != block.AIR.id):
                position.y = position.y + 1
        # Now apply appropriate jump to new position
        if (jump == 1):
            # Jump regardless
            position.y = position.y + 1
            mc.postToChat("JUMP : Pressed")
        # long jump uses getSafePos
        if (jump == 3):
            position = getSafePos(position.x, position.y, position.z)
            mc.postToChat("LONG JUMP : Pressed")
        # Now we have the position to move to, check it's not a solid block
        block_id = mc.getBlock(position)
        if (block_id == block.AIR.id):
            mc.player.setTilePos(position)
        # Otherwise not a valid move so ignore
        
        # Delay before next instruction
        time.sleep(DELAY)


# Find nearest empty block based on an x, z position
def getSafePos(x_pos, y_pos, z_pos):
    block_id = mc.getBlock(x_pos, y_pos, z_pos)
    # If y position is in the air then move down to find the first non-air block
    if (block_id == block.AIR.id):
        while (block_id == block.AIR.id):
            y_pos = y_pos - 1
            block_id = mc.getBlock(x_pos, y_pos, z_pos)
        # we have found the first solid block - we want to go one above that on the first air block
        y_pos = y_pos + 1
    # If y position is underground then count up to find the first air block
    else :
        while (block_id != block.AIR.id):
            y_pos = y_pos + 1
            block_id = mc.getBlock(x_pos, y_pos, z_pos)
    # Return full address
    return (x_pos, y_pos, z_pos)


#Run the main function when this program is run
if __name__ == "__main__":
    main()


