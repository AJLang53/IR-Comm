import time, math
import pigpio
import ir_tx
from CPR import CPR
import argparse

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

if __name__ == '__main__':
    
    # Transmit Parameters
    carrierHz = 1666.6666666666*2
    bitSize = 300   # The time size of the on cycle
    pulseNum = 1  # Number of cycles of carrier to fill bitSize
    gpio = 23


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
    altBase = 100
    NZ = 15
    lat = float(raw_input("Latitude: "))
    lon = float(raw_input("Longitude: "))
    alt = float(raw_input("Altitude: "))

    # Create the binary lat and lon in CPR format
    cpr = CPR()
    evenLoc = cpr.encode(lat, lon, 0)
    evenLat = bin(evenLoc[0])[2:]
    evenLon = bin(evenLoc[1])[2:]
    oddLoc = cpr.encode(lat, lon, 1)
    oddLat = bin(oddLoc[0])[2:]
    oddLon = bin(oddLoc[1])[2:]

    while len(evenLat)<17:
        evenLat = '0'+evenLat
    while len(evenLon)<17:
        evenLon = '0'+evenLon
    while len(oddLat)<17:
        oddLat = '0'+oddLat
    while len(oddLon)<17:
        oddLon = '0'+oddLon

    # Create the binary altitude in CPR format
    cprAlt = cpr.encodeAlt(alt, altBase)
        
    # Create the Type code, surveillance status, NIC supplement-B, and Time binary
    TC = bin(11)[2:]
    while len(TC)<5:
        TC = '0'+TC
    SS = bin(0)[2:]
    while len(SS)<2:
        SS = '0'+SS
    NICsB = bin(0)[2:]
    T = bin(0)[2:]

    # Assemble the data binary (56 bits)
    evenDataBin = TC+SS+NICsB+cprAlt+T+'0'+evenLat+evenLon
    oddDataBin = TC+SS+NICsB+cprAlt+T+'1'+oddLat+oddLon

    # Create the parity and add it to the message
    evenParityBin = crc(preamble+evenDataBin)
    oddParityBin = crc(preamble+oddDataBin)
    evenTrans = preamble+evenDataBin+evenParityBin
    oddTrans = preamble+oddDataBin+oddParityBin

    while len(evenTrans)<112:
        evenTrans = '0'+evenTrans
    while len(oddTrans)<112:
        oddTrans = '0'+oddTrans

    print("ADS-B Even Transmission: "+evenTrans)
    print("ADS-B Odd Transmission: "+oddTrans)
    print('\n')

    # Set up for transmitting
    pi = pigpio.pi()
    tx = ir_tx.tx(pi, gpio, carrierHz, False)

    # Create and begin sending
    try:
        while True:
            tx.clear_code()
            tx.add_to_wave(pulseNum, pulseNum)

            k=0
            while k < len(evenTrans):
                if evenTrans[k] == '1':
                    tx.add_to_wave(pulseNum, pulseNum)
                elif evenTrans[k] == '0':
                    tx.add_to_wave(0, pulseNum)
                    tx.add_to_wave(pulseNum, 0)
                k+=1

            tx.send_wave()
            
            tx.clear_code()


            time.sleep(0.1) # 100 ms between even and odd tranmissions
            
            tx.add_to_wave(pulseNum, pulseNum)
            k=0
            while k < len(oddTrans):
                if oddTrans[k] == '1':
                    tx.add_to_wave(pulseNum, pulseNum)
                elif oddTrans[k] == '0':
                    tx.add_to_wave(0, pulseNum)
                    tx.add_to_wave(pulseNum, 0)
                k+=1

            tx.send_wave()
            pi.wave_clear()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pi.stop()
        print("Stopped")
