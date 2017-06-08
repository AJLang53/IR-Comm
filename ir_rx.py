import pigpio
import time

class rx:

    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.high = False
        
        self.bits = []
        self.curBit = []
        
        self.pi.set_mode(self.gpio, pigpio.INPUT)
        cb_rising = self.pi.callback(self.gpio, pigpio.RISING_EDGE, self.rising)
        cb_falling = self.pi.callback(self.gpio, pigpio.FALLING_EDGE, self.falling)
        
    def rising(self):
        if not self.high:
            if len(curBit) != 0:
                self.curBit[2] = self.pi.get_current_tick()
                self.bits.append(self.curBit)
                self.curBit = []
            else:
                self.curBit[0] = self.pi.get_current_tick()
        self.high = True
        
    def falling(self):
        if self.high:
            self.curBit[1] = self.pi.get_current_tick()
        
