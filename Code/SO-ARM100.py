from sdl3 import *
from enum import Enum
from tqdm.auto import tqdm
from ctypes import c_int, pointer
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus
from lerobot.common.robot_devices.motors.feetech import TorqueMode
from lerobot.common.robot_devices.robots.configs import So100RobotConfig
from lerobot.common.robot_devices.robots.manipulator import ManipulatorRobot

leader_arm_config = FeetechMotorsBusConfig(
    port = "/dev/tty.usbmodem58FA0921301",
    motors = {
        "shoulder_pan": [1, "sts3215"],
        "shoulder_lift": [2, "sts3215"],
        "elbow_flex": [3, "sts3215"],
        "wrist_flex": [4, "sts3215"],
        "wrist_roll": [5, "sts3215"],
        "gripper": [6, "sts3215"],
    }
)

follower_arm_config = FeetechMotorsBusConfig(
    port = "/dev/tty.usbmodem58FD0171551",
    motors = {
        "shoulder_pan": [1, "sts3215"],
        "shoulder_lift": [2, "sts3215"],
        "elbow_flex": [3, "sts3215"],
        "wrist_flex": [4, "sts3215"],
        "wrist_roll": [5, "sts3215"],
        "gripper": [6, "sts3215"],
    },
)

### ROTATION +/- AND DIRECTIONS ###
# 0. LEFT_RIGHT        : works as one would expect from maths -ve = turn left; +ve = turns right.
# 1. SHOULDER          : +ve = forward; -ve = backwards.
# 2. ELBOW             : +ve = down; -ve = up.
# 3. WRIST_UP_DOWN     : +ve = down; -ve = up.
# 4. WRIST_ROTATION    : +ve = rotate rigth; -ve = rotate left.
# 5. GRIPPER           : +ve = open; -ve = close.

class Motors(Enum):
    LEFT_RIGHT = 0,
    SHOULDER = 1,
    ELBOW = 2,
    WRIST_UP_DOWN = 3
    WRIST_ROTATION = 4,
    GRIPPER = 5

def sdl_event_handling(e: SDL_Event):
    while SDL_PollEvent(pointer(e)):
        if e.type == SDL_EVENT_QUIT:
            running = False

        elif e.type == SDL_EVENT_KEY_DOWN:
            if e.key.key == SDLK_ESCAPE:
                running = False

def controller_operate(follower_arm: FeetechMotorsBus):
    running = True
    JOYSTICK_DEAD_ZONE = 8000

    SDL_Init(SDL_INIT_GAMEPAD)
    gamepads = SDL_GetGamepads(None)

    if gamepads[0]:
        gamepad = SDL_OpenGamepad(gamepads[0])

    else:
        print("No, Gamepad connected!")
        sys.exit()

    e = SDL_Event()
    while running:
        sdl_event_handling(e)

        left_x = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_LEFTX)
        left_y = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_LEFTY)
        right_x = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHTX)
        right_y = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHTY)
        l2 = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_LEFT_TRIGGER)
        r2 = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER)

        l1 = int(SDL_GetGamepadButton(gamepad,SDL_GAMEPAD_BUTTON_LEFT_SHOULDER))
        r1 = -SDL_GetGamepadButton(gamepad, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER)

        # Left Joystick
        if left_x < -JOYSTICK_DEAD_ZONE:
            left_x_dir = -10
        elif left_x > JOYSTICK_DEAD_ZONE:
            left_x_dir = 10
        else:
            left_x_dir = 0

        if left_y < -JOYSTICK_DEAD_ZONE:
            left_y_dir = -10
        elif left_y > JOYSTICK_DEAD_ZONE:
            left_y_dir = 10
        else:
            left_y_dir = 0

        # Right Joystick
        if right_x < -JOYSTICK_DEAD_ZONE:
            right_x_dir = -10
        elif right_x > JOYSTICK_DEAD_ZONE:
            right_x_dir = 10
        else:
            right_x_dir = 0

        if right_y < -JOYSTICK_DEAD_ZONE:
            right_y_dir = -10
        elif right_y > JOYSTICK_DEAD_ZONE:
            right_y_dir = 10
        else:
            right_y_dir = 0

        # L2/R2
        if l2 < JOYSTICK_DEAD_ZONE:
            l2_dir = 0
        else:
            l2_dir = -10

        if r2 < JOYSTICK_DEAD_ZONE:
            r2_dir = 0
        else:
            r2_dir = 10


        follower_arm.write("Torque_Enable", TorqueMode.ENABLED.value)
        position = follower_arm.read("Present_Position")

        position[Motors.LEFT_RIGHT.value] += (10*right_x_dir)
        position[Motors.SHOULDER.value] += (10*right_y_dir)
        position[Motors.ELBOW.value] += 10*(l2_dir + r2_dir)
        position[Motors.WRIST_ROTATION.value] -= (10*left_x_dir)
        position[Motors.WRIST_UP_DOWN.value] += (10*left_y_dir)
        position[Motors.GRIPPER.value] += 100*(l1 + r1)
        follower_arm.write("Goal_Position", position)

    follower_arm.write("Torque_Enable", TorqueMode.DISABLED.value)
    print("Ending Controller Movement!")

def move_computationally(follower_arm: FeetechMotorsBus, motor: Motors, amount: int):
    follower_arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    position = follower_arm.read("Present_Position")
    position[motor.value] += amount
    follower_arm.write("Goal_Position", position)
    follower_arm.write("Torque_Enable", TorqueMode.DISABLED.value)

def main():
    teleoperate = False
    move_with_controller = True

    leader_arm = FeetechMotorsBus(leader_arm_config)
    follower_arm = FeetechMotorsBus(follower_arm_config)

    leader_arm.connect()
    follower_arm.connect()

    leader_starting_position = leader_arm.read("Present_Position")
    follower_starting_position = follower_arm.read("Present_Position")

    print(f"Leader Starting Position - {leader_starting_position}")
    print(f"Follower Starting Position - {follower_starting_position}")

    robot_config = So100RobotConfig(
        leader_arms={"main": leader_arm_config},
        follower_arms={"main": follower_arm_config},
        cameras={}
    )
    robot = ManipulatorRobot(robot_config)
    robot.connect()

    while teleoperate:
        robot.teleop_step()

    if move_with_controller:
        controller_operate(follower_arm)

    leader_arm.disconnect()
    follower_arm.disconnect()

if __name__ == "__main__":
    main()