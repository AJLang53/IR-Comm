import time, math
import pigpio
import ir_tx
from CPR import CPR

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
cpr = CPR()
evenLoc = bin(cpr.encode(lat, lon, 0))[2:]
oddLoc = bin(cpr.encode(lat, lon, 1))[2:]

# Create the binary altitude in CPR format
cprAlt = cpr.encodeAlt(alt, altBase)
    
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
