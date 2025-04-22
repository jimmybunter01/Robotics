from sdl3 import *
from ctypes import c_int, pointer

SDL_Init(SDL_INIT_GAMEPAD)
gamepads = SDL_GetGamepads(None)

if gamepads[0]:
    gamepad = SDL_OpenGamepad(gamepads[0])

else:
    print("No, Gamepad connected!")
    sys.exit()

running = True
JOYSTICK_DEAD_ZONE = 8000

# TODO (JWG 22/04/2025 - 09:45) : May need a way to get magnitude of movement?
e = SDL_Event()
while running:
    while SDL_PollEvent(pointer(e)):
        if e.type == SDL_EVENT_QUIT:
            running = False
        elif e.type == SDL_EVENT_JOYSTICK_AXIS_MOTION:
            left_x = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_LEFTX)
            left_y = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_LEFTY)
            right_x = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHTX)
            right_y = SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHTY)

            # Left Joystick
            if left_x < -JOYSTICK_DEAD_ZONE:
                left_x_dir = -1
            elif left_x > JOYSTICK_DEAD_ZONE:
                left_x_dir = 1
            else:
                left_x_dir = 0

            if left_y < -JOYSTICK_DEAD_ZONE:
                left_y_dir = -1
            elif left_y > JOYSTICK_DEAD_ZONE:
                left_y_dir = 1
            else:
                left_y_dir = 0

            # Right Joystick
            if right_x < -JOYSTICK_DEAD_ZONE:
                right_x_dir = -1
            elif right_x > JOYSTICK_DEAD_ZONE:
                right_x_dir = 1
            else:
                right_x_dir = 0

            if right_y < -JOYSTICK_DEAD_ZONE:
                right_y_dir = -1
            elif right_y > JOYSTICK_DEAD_ZONE:
                right_y_dir = 1
            else:
                right_y_dir = 0

            print(left_x_dir)
            print(left_y_dir)
            print(right_x_dir)
            print(right_y_dir)