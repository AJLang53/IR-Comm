import pigpio

class rx:

    def __init__(self, pi, gpio, dig1, dig0, startBit, totalBits):
        self.pi = pi
        self.gpio = gpio
        self.dig1 = dig1
        self.dig0 = dig0
        self.startBit = startBit
        self.totalBits = totalBits
        self.high = False
        
        self.transmissions = []
        self.bits = []
        self.curBit = []
        
        self.pi.set_mode(self.gpio, pigpio.INPUT)
        cb_rising = self.pi.callback(self.gpio, pigpio.RISING_EDGE, self.rising)
        cb_falling = self.pi.callback(self.gpio, pigpio.FALLING_EDGE, self.falling)
        
    def rising(self, gpio, level, tick):
        if not self.high:
            if len(curBit) != 0:
                self.curBit[2] = self.pi.get_current_tick()
                self.bits.append(self.curBit)
                self.curBit = []
                self.curBit[0] = tick
            else:
                self.curBit[0] = tick
        self.high = True
        
    def falling(self):
        if self.high:
            self.curBit[1] = self.pi.get_current_tick()
            
    def received(self):
        return self.received
    
    def getTransmission(self):
        return self.bits
        
