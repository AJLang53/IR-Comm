import pigpio
import RPi.GPIO as GPIO
from datetime import datetime

class rx_pigpio:

    def __init__(self, pi, gpio, dig1, dig0, startBit, dataBits,addressBits):
        """
        Constructor. Sets the GPIO pin to input mode, and connects callbacks to rising and falling edge events
        """
        self.pi = pi
        self.gpio = gpio
        self.dig1 = dig1    # Length of digital 1
        self.dig0 = dig0    # Length of digital 0
        self.startBit = startBit    # Length of start bit
        self.dataBits = dataBits    # Total number of data bits
        self.addressBits = addressBits  # Total number of address bits
        
        self.tol = 100      # 100 microsecond tolerance
        self.started = False
        self.high = False
        self.riseTime = 0
        self.transmissions = []
        self.bits = []
        
        self.pi.set_mode(self.gpio, pigpio.INPUT)
        cb_rising = self.pi.callback(self.gpio, pigpio.RISING_EDGE, self.rising)
        cb_falling = self.pi.callback(self.gpio, pigpio.FALLING_EDGE, self.falling)
        
    def rising(self, gpio, level, tick):
        """
        Callback function for rising edge
        """
        
        if not self.high:
            self.riseTime = tick
            
        self.high = True
        
    def falling(self, gpio, level, tick):
        """
        Callback function for falling edge
        """
        
        # If there was a previous rising edge, but no start bit, check for a start bit
        if self.high and not self.started:
            timeHigh = pigpio.tickDiff(self.riseTime, tick)
            if abs(timeHigh - self.startBit) < self.tol:
                self.started = True
        
        # If there was a previous rising edge and start bit, determine if it's a 1 or 0
        elif self.high and self.started:
            timeHigh = pigprio.tickDiff(self.riseTime, tick)
            if abs(timeHigh - self.dig1) < self.tol:
                self.bits.append('1')
            else
                self.bits.append('0')
                
            # If all of the bits are received, add it to transmissions and reset bits
            if len(self.bits) == (self.dataBits + self.addressBits)
                self.transmissions.append(self.bits)
                self.bits = []
                
        self.high = False
            
    def received(self):
        """
        Return transmission state
        """
        
        if len(self.transmissions) != 0:
            return True
        else
            return False
    
    def getTransmission(self):
        """
        Return the oldest transmission as a tuple of (data, address) and removes it
        """
        
        trans = self.transmissions.pop(0)
        transData = trans[0:dataBits]
        transAddress = trans[dataBits:]
            
        return (transData, transAddress)
    
class rx_rpi_gpio:

    def __init__(self, gpio, dig1, dig0, startBit, dataBits,addressBits):
        """
        Constructor. Sets the GPIO pin to input mode, and connects callbacks to rising and falling edge events
        """
        
        self.gpio = gpio
        self.dig1 = dig1    # Length of digital 1
        self.dig0 = dig0    # Length of digital 0
        self.startBit = startBit    # Length of start bit
        self.dataBits = dataBits    # Total number of data bits
        self.addressBits = addressBits  # Total number of address bits
        
        self.tol = 100      # 100 microsecond tolerance
        self.started = False
        self.high = False
        self.riseTime = 0
        self.transmissions = []
        self.bits = []
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.IN)
        GPIO.add_event_detect(self.gpio,GPIO_RISING, callback=self.rising)
        GPIO.add_event_detect(self.gpio,GPIO_FALLING, callback=self.falling)
        
    def rising(self):
        """
        Callback function for rising edge
        """
        
        if not self.high:
            self.riseTime = datetime.now()
            
        self.high = True
        
        
    def falling(self):
        """
        Callback function for falling edge
        """
        
        # If there was a previous rising edge, but no start bit, check for a start bit
        if self.high and not self.started:
            timeHigh = datetime.now() - self.riseTime
            if abs(timeHigh.microseconds - self.startBit) < self.tol:
                self.started = True
        
        # If there was a previous rising edge and start bit, determine if it's a 1 or 0
        elif self.high and self.started:
            timeHigh = datetime.now() - self.riseTime
            if abs(timeHigh.microseconds - self.dig1) < self.tol:
                self.bits.append('1')
            else
                self.bits.append('0')
                
            # If all of the bits are received, add it to transmissions and reset bits
            if len(self.bits) == (self.dataBits + self.addressBits)
                self.transmissions.append(self.bits)
                self.bits = []
                
        self.high = False  
        
        

