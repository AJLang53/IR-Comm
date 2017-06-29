import math

class CPR:
    """
    Class to manage CPR encoding and decoding (global and local).
    Functions from gr-air-modes (github.com/bistromath/gr-air-modes)
    """

    def __init__(self, zones = 15):
        
        self.zones = zones
            
    def nz(self,ctype):
        return 4 * self.zones - ctype

    def dlat(self, ctype, surface = False):
        if surface ==1:
            tmp = 90.0
        else:
            tmp = 360.0

        nzcalc = self.nz(ctype)
        if nzcalc == 0:
            return tmp
        else:
            return tmp / nzcalc

    def nl(self, lat):
        if abs(lat) >= 87.0:
            return 1.0
        return math.floor( (2.0*math.pi) * math.acos(1.0- (1.0-math.cos(math.pi/(2.0*self.zones))) / math.cos( (math.pi/180.0)*abs(lat) )**2 )**-1)

    def dlon(self, declat_in, ctype, surface):
        if surface:
            tmp = 90.0
        else:
            tmp = 360.

        nlcalc = max(self.nl(declat_in) - ctype,1)
        return tmp / nlcalc

    def encode(self, lat, lon, ctype, surface = False):

        # Surface has 19 bits, airborne has 17
        if surface is True:
            scalar = 2.**19
        else:
            scalar = 2.**17

        dlati = self.dlat(ctype, False)
        yz = math.floor(scalar* ((lat % dlati)/dlati) + 0.5)
        rLat = dlati * ((yz / scalar) + math.floor(lat / dlati))

        #encode using 360 constant for segment size.
        dloni = self.dlon(lat, ctype, False)
        xz = math.floor(scalar * ((lon % dloni)/dloni) + 0.5)

        yz = int(yz) & (2**17-1)
        xz = int(xz) & (2**17-1)

        return (yz, xz) #lat, lon

    def roundTo(self, n,base):
        return int(round(base*round(n/base),2))

    def encodeAlt(self, alt, altBase = 25):

        # Round the alt to the base
        altCPRInt = int((self.roundTo(alt,altBase)+1000)/altBase)
        altCPR = bin(altCPRInt)[2:]

        # Add the base bit
        if altBase == 25:
            altCPR = altCPR[0:-4]+'1'+altCPR[-4:]
        elif altBase == 100:
            altCPR = altCPR[0:-4]+'0'+altCPR[-4:]

        # 12 bits
        while len(altCPR)<12:
            altCPR = '0'+altCPR

        return altCPR

    def decodeAlt(self,altCPR):
        altBase = int(altCPR[-5])
        print(altBase)
        if altBase == 1:
            altBase = 25
        else:
            altBase = 100

        altCPR = int(altCPR[0:-5]+altCPR[-4:],2)
        return altCPR*altBase - 1000
        
        

    def decodeGlobal(self, evenPos, oddPos, myPos=None, mostRecent=0, surface = False):
            
        #cannot resolve surface positions unambiguously without knowing receiver position
        if surface and myPos is None:
            return -1
        
        dLatEven = self.dlat(0, surface)
        dLatOdd  = self.dlat(1, surface)

        evenPos = [float(evenPos[0]), float(evenPos[1])]
        oddPos = [float(oddPos[0]), float(oddPos[1])]

        j = math.floor(((self.nz(1)*evenPos[0] - self.nz(0)*oddPos[0])/2**17) + 0.5) #latitude index

        rLatEven = dLatEven * ((j % self.nz(0)) + evenPos[0]/2**17)
        rLatOdd  = dLatOdd  * ((j % self.nz(1)) + oddPos[0]/2**17)

        #limit to -90, 90
        if rLatEven > 270.0:
            rLatEven -= 360.0
        if rLatOdd > 270.0:
            rLatOdd -= 360.0

        #This checks to see if the latitudes of the reports straddle a transition boundary
        #If so, you can't get a globally-resolvable location.
        if self.nl(rLatEven) != self.nl(rLatOdd):
            return -1

        if mostRecent == 0:
            rLat = rLatEven
        else:
            rLat = rLatOdd

        #disambiguate latitude
        if surface:
                if myPos[0] < 0:
                    rLat -= 90

        dl = self.dlon(rLat, mostRecent, surface)
        nl_rLat = self.nl(rLat)

        m = math.floor(((evenPos[1]*(nl_rLat-1)-oddPos[1]*nl_rLat)/2**17)+0.5) #longitude index

        #when surface positions straddle a disambiguation boundary (90 degrees),
        #surface decoding will fail. this might never be a problem in real life, but it'll fail in the
        #test case. the documentation doesn't mention it.

        if mostRecent == 0:
            encLon = evenPos[1]
        else:
            encLon = oddPos[1]

        rLon = dl * ((m % max(nl_rLat-mostRecent,1)) + encLon/2.**17)

        #print "DL: %f nl: %f m: %f rlon: %f" % (dl, nl_rlat, m, rlon)
        #print "evenpos: %x, oddpos: %x, mostrecent: %i" % (evenpos[1], oddpos[1], mostrecent)

        if surface:
            #longitudes need to be resolved to the nearest 90 degree segment to the receiver.
            wat = myPos[1]
            if wat < 0:
                wat += 360
            zone = lambda lon: 90 * (int(lon) / 90)
            rLon += (zone(wat) - zone(rLon))

        #limit to (-180, 180)
        if rLon > 180:
            rLon -= 360.0

        return [rLat, rLon]

    def decodeLat(self, encLat, ctype, myLat, surface=False):
        tmp1 = self.dlat(ctype, surface)
        tmp2 = float(encLat) / (2**17)
        j = math.floor(myLat/tmp1) + math.floor(0.5 + ((myLat % tmp1) / tmp1) - tmp2)

        return tmp1 * (j + tmp2)

    def decodeLon(self, decLat, encLon, ctype, myLon, surface=False):
        tmp1 = self.dlon(decLat, ctype, surface)
        tmp2 = float(encLon) / (2**17)
        m = math.floor(myLon / tmp1) + math.floor(0.5 + ((myLon % tmp1) / tmp1) - tmp2)

        return tmp1 * (m + tmp2)

    def decodeLocal(self, myLoc, encLoc, ctype, surface=False):
        [myLat, myLon] = myLoc
        [encLat, encLon] = encLoc

        decLat = self.decodeLat(encLat, ctype, myLat, surface)
        decLon = self.decodeLon(decLat, encLon, ctype, myLon, surface)

        return [decLat, decLon]


if __name__ == '__main__':
    cpr = CPR()
    lat = 15
    lon = -27
    alt = 1234
    evenLoc = cpr.encode(lat, lon, 0)
    oddLoc = cpr.encode(lat, lon, 1)
    myLoc = (45,-93)
    print(cpr.decodeGlobal(evenLoc,oddLoc))
    print(cpr.decodeLocal(myLoc, evenLoc, 0))
    print(cpr.decodeLocal(myLoc, oddLoc, 1))
    origAlt = cpr.encodeAlt(alt)
    print(int(origAlt[0:-5]+origAlt[-4:],2)*25 - 1000)
    

        
        
