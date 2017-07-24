import time
import pigpio
import ir_tx

pi = pigpio.pi()

tx = ir_tx.tx(pi, 18, 38000)

msg = int(raw_input("Message (0-127): "))   # 7 bit message
adr = int(raw_input("Address (0-32): "))    # 5 bit address

msgB = bin(msg)[2:]
adrB = bin(adr)[2:]

while len(msgB)<7:
    msgB = '0'+msgB
while len(adrB)<5:
    adrB = '0'+adrB

trans = msgB+adrB
print('Sending: '+str(trans))

tx.clear_code()
tx.add_to_wave(92, 23)  # 2400 ms start bit

k=0
while k< len(trans):
    if trans[k] == '1':
        tx.add_to_wave(46, 23)  # 1200 ms for digital 1
    elif trans[k] == '0':
        tx.add_to_wave(23, 23)  # 600 ms for digital 0
    k+=1

tx.send_wave()

tx.clear_code()

pi.stop()
print("Finished")
