import time, math
import pigpio
import ir_tx
from CPR import CPR
import argparse
import threading, Queue
import serial
import serial.tools.list_ports

class GPSThread(threading.Thread):
    """ A thread to read in raw GPS information, and organize it for the main thread """
    def __init__(self, threadID, gps, Q, exceptions, resetFlag,loggingGPS):			# Constructor
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.gpsSer = gps
        self.gpsQ = Q
        self.exceptionsQ = exceptions
        self.resetFlagQ = resetFlag
        self.loggingGPS = loggingGPS

    def run(self):
        global folder
        try:
            while True:					# Run forever
                line = self.gpsSer.readline()
                if(line.find("GPGGA") != -1):		# GPGGA indicates it's the GPS stuff we're looking for
                    try:
                        ### Parse the GPS Info ###
                        line = line.split(',')
                        if(line[1] == ''):
                            hours = 0
                            minutes = 0
                            seconds = 0
                        else:
                            hours = int(line[1][0:2])
                            minutes = int(line[1][2:4])
                            seconds = int(line[1][4:].split('.')[0])
                        if(line[2] == ''):
                            lat = 0
                        else:
                            lat = float(line[2][0:2]) + (float(line[2][2:]))/60
                        if(line[4] == ''):
                            lon = 0
                        else:
                            lon = -(float(line[4][0:3]) + (float(line[4][3:]))/60)
                        if(line[9] == ''):
                            alt = 0
                        else:
                            alt = float(line[9])
                        sat = int(line[7])
                        
                        ### Organize the GPS info, and put it in the queue ###
                        gpsStr = str(hours)+','+ str(minutes)+','+ str(seconds)+','+ str(lat)+','+str(lon)+','+str(alt)+','+str(sat)+'!'+'\n'
                        gpsCoords = (lat, lon, alt)
                        self.gpsQ.put(gpsCoords)

                        if self.loggingGPS:
                            try:
                                f = open(folder+"gpslog.txt","a")
                                f.write(gpsStr)
                                f.close()
                            except Exception, e:
                                print("Error logging GPS")
                                self.exceptionsQ.put(str(e))
                
                    except Exception,e:
                        self.exceptionsQ.put(str(e))
                        
        ### Catches unexpected errors ###
        except Exception, e:
            self.exceptionsQ.put(str(e))
            self.resetFlagQ.put('gpsThread dead')


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

    folder = '/gpsLogs/'
    loggingGPS = False

    ports = serial.tools.list_ports.comports()
    for each in ports:
        if each.vid == 4292 and each.pid == 60000:
            gps = serial.Serial(port = each.device, baudrate = 9600, timeout = 5)

    gpsQ = Queue.LifoQueue()
    gpsResetQ = Queue.Queue()
    gpsExceptionsQ = Queue.Queue()

    gpsThread = GPSThread("gpsThread",gps,gpsQ,gpsExceptionsQ,gpsResetQ,loggingGPS)
    gpsThread.daemon = True
    gpsThread.start()
    
    # Transmit Parameters
    carrierHz = 38000
    bitSize = 225   # The time size of the on cycle
    pulseNum = bitSize/(1000000/carrierHz)  # Number of cycles of carrier to fill bitSize
    gpio = 18
    altBase = 25
    NZ = 15

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
        
    # Create the Type code, surveillance status, NIC supplement-B, and Time binary
    TC = bin(11)[2:]
    while len(TC)<5:
        TC = '0'+TC
    SS = bin(0)[2:]
    while len(SS)<2:
        SS = '0'+SS
    NICsB = bin(0)[2:]
    T = bin(0)[2:]

    # Set up for transmitting
    pi = pigpio.pi()
    tx = ir_tx.tx(pi, gpio, carrierHz)

    lat = 10.0
    lon = 10.0
    alt = 10.0

    # Create and begin sending
    try:
        start = time.time()
        while True:

            # Get the newest GPS location
            if not gpsQ.empty():
                coords = gpsQ.get()
                while not gpsQ.empty():
                    gpsQ.get()

                lat = coords[0]
                lon = coords[1]
                alt = coords[2]

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

##            print("ADS-B Even Transmission: "+evenTrans)
##            print("ADS-B Odd Transmission: "+oddTrans)
##            print('\n')
            delay = time.time()            
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
            delay = time.time()
            tx.clear_code()


            while (time.time() - delay)<0.02:
                pass
##            time.sleep(0.1) # 100 ms between even and odd tranmissions
            
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
            delay = time.time()
            pi.wave_clear()
            while (time.time() - delay)<0.02:
                pass
##            time.sleep(0.1)
            print(time.time()-start)
            start = time.time()
    except KeyboardInterrupt:
        pi.stop()
        print("Stopped")
