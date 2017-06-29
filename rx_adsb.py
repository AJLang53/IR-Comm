import RPi.GPIO as GPIO
from datetime import datetime

def crc(msg, encode = False):
    GENERATOR = '1111111111111010000001001'
    msgbin = list(msg)
    
    if encode:
        msgbin[-24:] = ['0']*24

    for i in range(len(msgbin)-24):
        if msgbin[i] == '1':
            for j in range(len(GENERATOR)):
                msgbin[i+j] = str((int(msgbin[i+j])^int(GENERATOR[j])))

    reminder = ''.join(msgbin[-24:])
    return reminder

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

bitSize = 225

while True:
    lvl = 1

    while lvl:
        lvl = GPIO.input(18)

    startTime = datetime.now()

    raw = []
    received = ''

    nomOnes = 0

    previousLvl = 0

    started = False
    toggle = False

    while True:
        if lvl != previousLvl:
            now = datetime.now()
            pulseLength = now - startTime
            startTime = now

            raw.append((previousLvl, pulseLength.microseconds))

            if abs(pulseLength.microseconds - bitSize) < bitSize/2:
                started = True

            if started:
                if abs(pulseLength.microseconds - bitSize) < bitSize/2:
                    if previousLvl == 0 and toggle == False:
                        received+='1'
                    elif previousLvl == 1 and toggle == True:
                        received+='0'
                elif abs(pulseLength.microseconds - (2*bitSize)) < bitSize/2:
                    if previousLvl == 1:
                        received+='0'
                        toggle = True
                    else:
                        received+='1'
                        toggle = False

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

    received=received[1:]

    # Parse the binary
    try:
        DF = int(received[0:5],2)
        EC = int(received[5:8],2)
        ICA024 = hex(int(received[8:32],2))
        data = received[32:88]
        TC = int(data[0:4],2)
        SS = int(data[4:5],2)
        NICsb = int(data[6],2)
        altCPR = data[7:19]
        T = int(data[20],2)
        cprOddEven = int(data[21],2)
        latCPR = int(data[22:39],2)*1.0     # Make lat and lon floats
        lonCPR = int(data[39:56],2)*1.0
        parity = received[88:]
    except:
        print("Error with received binary")

    checksum = crc(parity)
    if checksum != parity:
        print("CORRUPTION")
    else:
        if DF == 17:
            if TC = 11:
                # Get the Lat and Lon in degrees
                dLat = 360/(NZ*4)
                origLat = dLat*(j+CPRLat/math.pow(2,17))
                dLon = 360/NL(origLat,NZ)
                m = math.floor(lonS/dLon) + math.floor(0.5 + (mod(lonS,dLon)/dLon) - XZ/math.pow(2,17))
                origLon = dLon*(m+CPRLon/math.pow(2,17))
                # Get the altitude in feet
                if altCPR[-5] == '1':
                    origAlt = int(altCPR[0:-5]+altCPR[-4:],2)*25 - 1000
                elif altCPR[-5] == '0':
                    origAlt = int(altCPR[0:-5]+altCPR[-4:],2)*100 - 1000

                print("Received Lat: "+str(origLat))
                print("Received Lon: "+str(origLon))
                print("Received Alt: "+str(origAlt))
            else:
                print("Wrong Type Code")
        else:
            print("Wrong data format")
    
