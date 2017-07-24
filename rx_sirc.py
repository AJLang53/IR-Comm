import RPi.GPIO as GPIO
from datetime import datetime

gpio = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio, GPIO.IN)

while True:
    lvl = 1

    while lvl:      # Receiver goes low when receiving
        lvl = GPIO.input(gpio)

    startTime = datetime.now()

    raw = []
    data = ''

    nomOnes = 0

    previousLvl = 0

    started = False
    dataReady = False

    while True:
        if lvl != previousLvl:      # If the level has changed, measure the pulse width
            now = datetime.now()
            pulseLength = now - startTime
            startTime = now

            raw.append((previousLvl, pulseLength.microseconds))
            
            # Process the pulse to determine corresponding bit (PWM, 2400 ms for start, 1200 ms for 1, 600 ms for 0)
            if abs(pulseLength.microseconds - 2400) < 600:
                started = True

            if started:
                if abs(pulseLength.microseconds - 1200) < 600:
                    data+='1'
                elif abs(pulseLength.microseconds - 600) < 300:
                    if dataReady:
                        data+='0'
                    else:
                        dataReady = True

        if lvl:
            numOnes = numOnes + 1

        else:
            numOnes = 0

        if numOnes > 10000:     # Timeout
            break

        previousLvl = lvl
        lvl = GPIO.input(gpio)
    transTime = 0
    print "Raw:"
    for (lvl, pulse) in raw:
        print lvl, pulse
        transTime += pulse

    interpData = ''
    while len(data) != 0:
        interpData+=data[0]
        data = data[2:]
    print("Data: "+interpData+'\n')
    print("Transmission Time: "+str(transTime))
    try:   # SIRC encoding standard has message and address
        print("Message: "+str(int(interpData[0:7],2)))
        print("Address: "+str(int(interpData[7:],2)))
    except Exception, e:
        pass
