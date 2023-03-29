import csv
import math
import os
import time

import pygame

# pygame init
from PID import PID

pygame.font.init()
pygame.mixer.init()
first_distance_from_moon = 13748  # 2:25:40 (as in the simulation) // https://www.youtube.com/watch?v=JJ0VfRL9AMs
first_dist = 181 * 1000
WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulating Bereshit's Landing")
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
FONT = pygame.font.SysFont('comicsans', 20)
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
MOON_HEIGHT = 100
SPACESHIP_IMAGE = pygame.image.load(
    os.path.join('images', 'spaceship.png'))
MOON_IMAGE = pygame.transform.scale(pygame.image.load(
    os.path.join('images', 'moon.png')), (WIDTH, MOON_HEIGHT))
SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join('images', 'space.png')), (WIDTH, HEIGHT))

# landing init
WEIGHT_EMP = 165  # kg
WEIGHT_FULE = 420  # kg
WEIGHT_FULL = WEIGHT_EMP + WEIGHT_FULE  # kg
MAIN_ENG_F = 430  # N
SECOND_ENG_F = 25  # N
MAIN_BURN = 0.15  # liter per sec, 12 liter per m'
SECOND_BURN = 0.009  # liter per sec 0.6 liter per m'
ALL_BURN = MAIN_BURN + 8 * SECOND_BURN

RADIUS = 3475 * 1000  # meters
ACC = 1.622  # m/s^2
EQ_SPEED = 1700  # m/s


def draw_window(spaceship, angle, data={}):
    WIN.blit(SPACE, (0, 0))
    text = FONT.render(f"Bereshit Spaceship", 1, RED)
    center = ((WIDTH - text.get_width()) * 0.5)
    WIN.blit(text, (center, 15))
    text = FONT.render(f"Landing Information:", 1, WHITE)
    WIN.blit(text, (10, 25))
    i = 2
    for k, v in data.items():
        text = FONT.render(f"{k}: {v}", 1, WHITE)
        WIN.blit(text, (10, i * 25))
        i += 1
    SPACESHIP = pygame.transform.rotate(pygame.transform.scale(SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)),
                                        angle)
    WIN.blit(MOON_IMAGE, (0, 800))
    WIN.blit(SPACESHIP, (spaceship.x, spaceship.y))
    pygame.display.update()


def spaceship_movement(distance, dist, spaceship):
    dx = dist / first_dist
    dy = distance / first_distance_from_moon
    spaceship.x = WIDTH - (WIDTH * dy) - MOON_HEIGHT
    spaceship.y = HEIGHT - HEIGHT * dy - MOON_HEIGHT


def accMax(weight: float) -> float:
    return acc(weight, True, 8)


def acc(weight: float, main: bool, seconds: int) -> float:
    t = 0
    if main:
        t += MAIN_ENG_F
    t += seconds * SECOND_ENG_F
    ans = t / weight
    return ans


def getAcc(speed):
    n = abs(speed) / EQ_SPEED
    ans = (1 - n) * ACC
    return ans


def csv_unique_name(folder='logs'):
    path = os.path.join(os.getcwd(), folder)
    try:
        os.mkdir(path)
    except:
        pass
    files = os.listdir(path)
    i = 1
    while 1:
        if f'log{i}.csv' not in files:
            return f'log{i}'
        i += 1


def makeCsv(l, folder='logs', csvname='bereshit_102'):
    path = os.path.join(os.getcwd(), folder)
    try:
        os.mkdir(path)
    except:
        pass
    f = open(f'{folder}/{csvname}.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerows(l)
    f.close()
    print(f'{csvname} saved.')


def calcDesiredSpeed(distance_from_moon, curr_speed):
    if curr_speed == 0:
        return distance_from_moon
    if distance_from_moon < 1000:
        print(f"Dist: {distance_from_moon}")
        print(f"Time: {distance_from_moon} / {curr_speed} = {distance_from_moon / curr_speed}")
        print(
            f"Desired: {curr_speed} - ({curr_speed} / ({distance_from_moon / curr_speed})) = {curr_speed - (curr_speed / (distance_from_moon / curr_speed))}")
        print("************************************************************************************")
    if distance_from_moon < 500:
        return 0

    time = distance_from_moon / curr_speed
    desired_speed = curr_speed - (curr_speed / time)
    if (desired_speed < 3): desired_speed = 0
    return desired_speed


def calcError(curr_speed, desired_speed):
    return curr_speed - desired_speed


def adjustAngle(curr_angle, desired_change):
    if curr_angle + desired_change < 3:
        return 0
    elif curr_angle + desired_change > 177:
        return 180
    else:
        return curr_angle + desired_change


def adjustSpeed(curr_NN, desired_change):
    if curr_NN + desired_change > 0.997:
        return 1
    elif curr_NN + desired_change < 0.003:
        return 0
    else:
        return curr_NN + desired_change


def main(simulation=1, first_distance_from_moon=first_distance_from_moon):
    tocsv = []
    spaceship = pygame.Rect(0, 0, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    # starting point:
    vertical_speed = 24.8
    horizontal_speed = 932
    dist = 181 * 1000
    angle = 58.3  # zero is vertical (as in landing)
    distance_from_moon = first_distance_from_moon
    _time = 0
    dt = 1  # sec
    acceleration = 0  # Acceleration rate (m/s^2)
    fuel = 121
    weight = WEIGHT_EMP + fuel
    print(f"simulation {simulation} started")
    if simulation == 1:
        print("Simulating Bereshit's Landing:")
        tocsv.append(
            ['time', 'vertical_speed', 'dvs', 'VP', 'VI', 'VD', 'VPID', 'horizontal_speed',
             'dist',
             'distance_from_moon', 'angle', 'weight',
             'acceleration', 'fuel'])
        print(tocsv[0])
    NN = 0.7  # rate[0,1]
    last_NN=NN
    desired_ver_speed = 25
    v_pid = PID(0.04, 0.0003, 0.2)

    v_pid_args = v_pid.run(vertical_speed, desired_ver_speed)
    vp = v_pid_args[0]
    vi = v_pid_args[1]
    vd = v_pid_args[2]
    v_tot = v_pid_args[3]
    last_v_tot = v_tot
    # ***** main simulation loop ******
    while distance_from_moon > 0:
        if simulation == 1:
            tocsv.append(
                [_time, vertical_speed, desired_ver_speed, vp, vi, vd, v_tot, horizontal_speed, dist,
                 distance_from_moon, angle, weight, acceleration, fuel])
            print(tocsv[-1])

        if distance_from_moon > 1000:
            if vertical_speed > 30 or vertical_speed < 20:
                NN = adjustSpeed(last_NN,last_v_tot)
            print("vertical PID\n")
            v_pid_args = v_pid.run(vertical_speed, desired_ver_speed)
            vp = v_pid_args[0]
            vi = v_pid_args[1]
            vd = v_pid_args[2]
            v_tot = v_pid_args[3]


        else:
            if angle != 0:
                angle = adjustAngle(angle, -3)
            if vertical_speed > 20:
                NN = 1
                print(f"NN: {NN}")
            elif 15 < vertical_speed <=20:
                NN = 0.7
            elif 2 < vertical_speed <= 15:
                NN= 0.6
            else:
                NN = 0
                print(f"NN: {NN}")

        if horizontal_speed < 2:
            horizontal_speed = 0
        last_v_tot = v_tot
        last_NN=NN

        if distance_from_moon == 0: break
        # main computations
        ang_rad = math.radians(angle)
        h_acc = math.sin(ang_rad) * acceleration
        v_acc = math.cos(ang_rad) * acceleration
        vacc = getAcc(horizontal_speed)
        _time += dt
        dw = dt * ALL_BURN * NN
        if fuel > 0:
            fuel -= dw
            weight = WEIGHT_EMP + fuel
            acceleration = NN * accMax(weight)

        else:  # ran out of fuel
            acceleration = 0

        v_acc -= vacc
        if horizontal_speed > 0:
            horizontal_speed -= h_acc * dt
        dist -= horizontal_speed * dt
        vertical_speed -= v_acc * dt
        distance_from_moon -= dt * vertical_speed

        # update gui
        spaceship_movement(distance_from_moon, dist, spaceship)
        data = {'time': round(_time, 2), 'vertical speed': round(vertical_speed, 2),
                'horizontal speed': round(horizontal_speed, 2), 'distance': round(distance_from_moon, 2),
                'weight': round(weight, 2), 'fuel': round(fuel, 2), 'angle': angle, 'NN': NN}
        draw_window(spaceship, angle, data)
        time.sleep(0.01)

    # making a csv file of the data
    if simulation == 1:
        makeCsv(tocsv, csvname=csv_unique_name())

    # show the results for 5 seconds
    time.sleep(10)

    # repeat the gui for 5 times
    if simulation == 5:
        pygame.quit()
        return
    main(simulation=simulation + 1)


if __name__ == '__main__':
    main()
