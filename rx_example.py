import pigpio
import threading, Queue
import ir_rx

pi = pigpio.pi()
transmissions = Queue.LifoQueue()
interrupt =  Queue.Queue()
rx = ir_rx.rx_pigpio(pi, 14, transmissions, interrupt, 1200, 600, 2400, 7, 5)  # SIRC protocol
rx.start()

while self.transmissions.empty():
    pass
    
trans = self.transmissions.get()
print("Data",trans[0])
print("Address",trans[1])

self.interrupt.put("stop")
pi.stop()
