import time
import pigpio
import ir_tx

carrierHz = 38000
bitSize = 300
pulseNum = bitSize/(1000000/carrierHz)

pi = pigpio.pi()
tx = ir_tx.tx(pi, 18, carrierHz)

msg = int(raw_input("Message (0-5.192296e33): "))

msgB = bin(msg)[2:]
trans=msgB

while len(trans)<112:
    trans = '0'+trans

print('Sending: '+str(trans))

tx.clear_code()
tx.add_to_wave(pulseNum, pulseNum)

k=0
while k< len(trans):
    if trans[k] == '1':
        tx.add_to_wave(pulseNum, pulseNum)
    elif trans[k] == '0':
        tx.add_to_wave(0, pulseNum)
        tx.add_to_wave(pulseNum, 0)
    k+=1

tx.send_wave()

tx.clear_code()

pi.stop()
print("Finished")
