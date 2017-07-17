import pigpio

pi = pigpio.pi()

pi.set_mode(18,pigpio.OUTPUT)
pi.write(18,0)
on = False
pi.write(18,1)
while True:
	input = raw_input()
	if input == '':
		if on:
			pi.write(18,0)
			on = False
		else:
			pi.write(18,1)
			on = True
	elif input == 'x':
		pi.write(18,0)
		pi.stop()
		break
exit()
