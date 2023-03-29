class PID:
    def __init__(self, p0, i0, d0):
        self.p0 = p0
        self.i0 = i0
        self.d0 = d0
        self.last_speed = 0
        self.integral = 0
        self.first_run = True

    def run(self, curr, desired):
        P = curr - desired
        D = curr - self.last_speed
        I = self.integral+P
        print(f"Self integral: {self.integral}\n")
        print(f"Curr: {curr}\n Desired: {desired}\n Last speed: {self.last_speed}\n P: {P}\n D: {D}\n I: {I}")
        self.integral =I
        if (self.first_run):
            D = 0
            self.first_run = False

        pid_calc = (self.p0 * P) + (self.i0 * I) + (self.d0 * D)
        self.last_speed=curr
        return (P, I, D, pid_calc)
