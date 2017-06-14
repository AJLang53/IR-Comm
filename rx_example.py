import pigpio
import ir_rx

pi = pigpio.pi()

rx = ir_rx.rx_pigpio(pi, 14, 1200, 600, 2400, 7, 5)  # SIRC protocol

while not rx.received:
    pass
    
trans = rx.getTransmission()
print("Data",trans[0])
print("Address",trans[1])

pi.stop()
