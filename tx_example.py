import time
import pigpio
import ir_tx

pi = pigpio.pi()

tx = ir_tx.tx(pi, 18, 38000)

tx.clear_code()

tx.add_to_wave(92, 23) # Start
tx.add_to_wave(46, 23) # 1
tx.add_to_wave(23, 23) # 0
tx.add_to_wave(23, 23) # 0
tx.add_to_wave(46, 23) # 1
tx.add_to_wave(23, 23) # 0
tx.add_to_wave(46, 23) # 1
tx.add_to_wave(23, 23) # 0
tx.add_to_wave(46, 23) # 1
tx.add_to_wave(23, 23) # 0
tx.add_to_wave(23, 23) # 0
tx.add_to_wave(46, 23) # 1
tx.add_to_wave(23, 23) # 0

tx.send_wave()
tx.clear_code()

pi.stop()
print("Finished")
