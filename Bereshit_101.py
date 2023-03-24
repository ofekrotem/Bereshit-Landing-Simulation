import math
import os
import csv
WEIGHT_EMP = 165  # kg
WEIGHT_FULE = 420  # kg
WEIGHT_FULL = WEIGHT_EMP + WEIGHT_FULE  # kg
MAIN_ENG_F = 430  # N
SECOND_ENG_F = 25  # N
MAIN_BURN = 0.15  # liter per sec, 12 liter per m'
SECOND_BURN = 0.009  # liter per sec 0.6 liter per m'
ALL_BURN = MAIN_BURN + 8 * SECOND_BURN


def accMax(weight: float) -> float:
    return acc(weight, True, 8)


def acc(weight: float, main: bool, seconds: int) -> float:
    t = 0
    if main:
        t += MAIN_ENG_F
    t += seconds * SECOND_ENG_F
    ans = t / weight
    return ans


RADIUS = 3475 * 1000  # meters
ACC = 1.622  # m/s^2
EQ_SPEED = 1700  # m/s


def getAcc(speed):
    n = abs(speed) / EQ_SPEED
    ans = (1 - n) * ACC
    return ans

def makeCsv(l,folder='logs',csvname='bereshit_102'):
    path = os.path.join(os.getcwd(), folder)
    try:
        os.mkdir(path)
    except:
        pass
    f = open(f'{folder}/{csvname}.csv', 'w',newline='')
    writer = csv.writer(f)
    print(l)
    writer.writerows(l)
    f.close()
    print(f'{csvname} saved.')

# 14095, 955.5, 24.8, 2.0 
if __name__ == '__main__':
    tocsv=[]
    print("Simulating Bereshit's Landing:")
    # starting point:
    vertical_speed = 24.8
    horizontal_speed = 932
    dist = 181 * 1000
    angle = 58.3  # zero is vertical (as in landing)
    distance_from_moon = 13748  # 2:25:40 (as in the simulation) // https://www.youtube.com/watch?v=JJ0VfRL9AMs
    time = 0
    dt = 1  # sec
    acceleration = 0  # Acceleration rate (m/s^2)
    fuel = 121
    weight = WEIGHT_EMP + fuel
    tocsv.append(['time', 'vertical_speed', 'horizontal_speed', 'dist', 'distance_from_moon', 'angle', 'weight', 'acceleration'])
    print(tocsv[0])
    NN = 0.7  # rate[0,1]


    # ***** main simulation loop ******
    while distance_from_moon > 0:
        if time % 10 == 0 or distance_from_moon < 100:
            tocsv.append([time, vertical_speed, horizontal_speed, dist, distance_from_moon, angle, weight, acceleration])
            print(tocsv[-1])
        # over 2 km above the ground
        if distance_from_moon > 2000:  # maintain a vertical speed of [20-25] m/s
            if vertical_speed > 25:
                NN += 0.003 * dt  # more power for braking
            if vertical_speed < 20:
                NN -= 0.003 * dt  # less power for braking
        # lower than 2 km - horizontal speed should be close to zero
        else:
            if angle > 3:
                angle -= 3  # rotate to vertical position.
            else:
                angle = 0
            NN = 0.5  # brake slowly, a proper PID controller here is needed!
            if horizontal_speed < 2:
                horizontal_speed = 0
            if distance_from_moon < 125:  # very close to the ground!
                NN = 1
                if vertical_speed < 5:
                    NN = 0.7  # if it is slow enough - go easy on the brakes
        if distance_from_moon < 5:  # no need to stop
            NN = 0.4
        # main computations
        ang_rad = math.radians(angle)
        h_acc = math.sin(ang_rad) * acceleration
        v_acc = math.cos(ang_rad) * acceleration
        vacc = getAcc(horizontal_speed)
        time += dt
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
makeCsv(tocsv)
