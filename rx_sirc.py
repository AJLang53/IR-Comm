import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

while True:
    lvl = 1

    while lvl:
        lvl = GPIO.input(18)

    startTime = datetime.now()

    raw = []
    data = ''

    nomOnes = 0

    previousLvl = 0

    started = False
    dataReady = False

    while True:
        if lvl != previousLvl:
            now = datetime.now()
            pulseLength = now - startTime
            startTime = now

            raw.append((previousLvl, pulseLength.microseconds))

            if abs(pulseLength.microseconds - 2400) <100:
                started = True

            if started:
                if abs(pulseLength.microseconds - 1200) < 100:
                    data+='1'
                elif abs(pulseLength.microseconds - 600) < 100:
                    if dataReady:
                        data+='0'
                    else:
                        dataReady = True

        if lvl:
            numOnes = numOnes + 1

        else:
            numOnes = 0

        if numOnes > 10000:
            break

        previousLvl = lvl
        lvl = GPIO.input(18)
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
    try:
        print("Message: "+str(int(interpData[0:7],2)))
        print("Address: "+str(int(interpData[7:],2)))
    except Exception, e:
        pass
