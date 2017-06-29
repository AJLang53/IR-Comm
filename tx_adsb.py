import time
import pigpio
import ir_tx
import math

def roundTo(n,base):
    return int(round(base*round(n/base),2))

def mod(x,y):
    return x-y*math.floor(x/y)

def NL(lat,NZ):
    try:
        num = 1-math.cos(math.pi/(2*NZ))
        den = math.pow(math.cos(math.pi/180 * abs(lat)),2)
        NL = math.floor(2*math.pi*math.pow(math.acos(1 - num/den),-1))
    except:
        print("NL Exception")
        return 1
    
    if NL < 1:
        return 1
    elif NL > 59:
        return 59
    else:
        return NL

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
    return reminderdef roundTo(n,base):

    
# Transmit Parameters
carrierHz = 38000
bitSize = 225   # The time size of the on cycle
pulseNum = bitSize/(1000000/carrierHz)  # Number of cycles of carrier to fill bitSize
gpio = 18


# Create the data format and emitter category binary
DF = 17
DFBin = bin(DF)[2:]
while len(DFBin)<5:
    DFBin = '0'+DFBin

EC = 5
ECBin = bin(EC)[2:]
while len(ECBin)<3:
    ECBin = '0'+ECBin

# Create the ICAO24 binary (unique aircraft ID)
ICAO24 = '101010101010101010101010'

# Create the preamble binary
preamble = DFBin+ECBin+ICAO24

# Location Information
altBase = 25
NZ = 15
lat = float(raw_input("Latitude: "))
lon = float(raw_input("Longitude: "))
alt = float(raw_input("Altitude: "))

# Create the binary lat and lon in CPR format
dLat = 360/(4*NZ)

YZ = math.floor(math.pow(2,17)*(mod(lat,dLat)/dLat) + 0.5)

RLat = dLat*(YZ/math.pow(2,17) + math.floor(lat/dLat))

dLon = 360/NL(RLat,NZ)

XZ = math.floor(math.pow(2,17)*(mod(lon,dLon)/dLon) + 0.5)

YZ = int(mod(YZ,math.pow(2,17)))
XZ = int(mod(XZ,math.pow(2,17)))

YZBin = bin(YZ)[2:]
while len(YZBin)<17:
    YZBin = '0'+YZBin
    
XZBin = bin(XZ)[2:]
while len(XZBin)<17:
    XZBin = '0'+XZBin

# Create the binary altitude in CPR format
altCPRInt = int((roundTo(alt,altBase)+1000)/altBase)
altCPR = bin(altCPRInt)[2:]
if altBase == 25:
    altCPR = altCPR[0:-4]+'1'+altCPR[-4:]
elif altBase == 100:
    altCPR = altCPR[0:-4]+'0'+altCPR[-4:]

while len(altCPR)<12:
    altCPR = '0'+altCPR
    
# Create the Type code, surveillance status, NIC supplement-B, Time, and CPR Odd/Even binary
TC = bin(11)[2:]
while len(TC)<5:o
    TC = '0'+TC
SS = bin(0)[2:]
while len(SS)<2:
    SS = '0'+SS
NICsB = bin(0)[2:]
T = bin(0)[2:]
F = bin(0)[2:]

# Assemble the data binary (56 bits)
dataBin = TC+SS+NICsB+altCPR+T+F+YZBin+XZBin

# Create the parity and add it to the message
parityBin = crc(preamble+dataBin)
print(parityBin)
trans = preamble+dataBin+parityBin

print("ADS-B Transmission: "+trans)
print('\n')

# Set up for transmitting
pi = pigpio.pi()
tx = ir_tx.tx(pi, gpio, carrierHz)

while len(trans)<112:
    trans = '0'+trans

# Create and Send the message
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
