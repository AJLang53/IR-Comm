import time
import pigpio
import ir_tx

pi = pigpio.pi()

tx = ir_tx.tx(pi, 23, 833.33333333)

msg = int(raw_input("Message (0-127): "))
adr = int(raw_input("Address (0-32): "))

msgB = bin(msg)[2:]
adrB = bin(adr)[2:]

##while len(msgB)<7:
##    msgB = '0'+msgB
##while len(adrB)<5:
##    adrB = '0'+adrB
##
##trans = msgB+adrB
##print('Sending: '+str(trans))
##
##tx.clear_code()
##tx.add_to_wave(4, 1)
##
##k=0
##while k< len(trans):
##    if trans[k] == '1':
##        tx.add_to_wave(2, 1)
##    elif trans[k] == '0':
##        tx.add_to_wave(1, 1)
##    k+=1

tx.add_to_wave(4,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(2,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(1,1)
tx.add_to_wave(2,1)
tx.add_to_wave(1,1)

tx.send_wave()

tx.clear_code()

pi.stop()
print("Finished")
