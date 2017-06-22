import pigpio

pi = pigpio.pi()

pi.set_mode(18,pigpio.OUTPUT)

while True:
	input = raw_input()
	if input == '1':
		pi.write(18,1)
	elif input == '0':
		pi.write(18,0)
	elif input == 'x':
		pi.write(18,0)
		pi.stop()
		break
exit()
