import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

bitSize = 300       # Must match transmitter

while True:
    lvl = 1
    
    while lvl:      # Receiver goes low when receiving
        lvl = GPIO.input(18)

    startTime = datetime.now()

    raw = []
    data = ''

    nomOnes = 0

    previousLvl = 0

    started = False
    toggle = False

    while True:
        if lvl != previousLvl:      # If the level has changed, measure the pulse width
            now = datetime.now()
            pulseLength = now - startTime
            startTime = now

            raw.append((previousLvl, pulseLength.microseconds))
            
            # Process the pulse to determine it's corresponding bit (PPM encoding)
            if abs(pulseLength.microseconds - bitSize) < bitSize/2:
                started = True

            if started:
                if abs(pulseLength.microseconds - bitSize) < bitSize/2:
                    if previousLvl == 0 and toggle == False:
                        data+='1'
                    elif previousLvl == 1 and toggle == True:
                        data+='0'
                elif abs(pulseLength.microseconds - (2*bitSize)) < bitSize/2:
                    if previousLvl == 1:
                        data+='0'
                        toggle = True
                    else:
                        data+='1'
                        toggle = False

        if lvl:
            numOnes = numOnes + 1

        else:
            numOnes = 0

        if numOnes > 10000:     # Timeout
            break

        previousLvl = lvl
        lvl = GPIO.input(18)
    transTime = 0
    print "Raw:"
    for (lvl, pulse) in raw:
        print lvl, pulse
        transTime += pulse

    data=data[1:]       # Remove the start bit

    print("\nBinary: "+data)
    print("Transmission Time: "+str(transTime))
    try:
        print("Decimal: "+str(int(data,2))+'\n')
    except Exception, e:
        pass
