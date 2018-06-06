# -*- coding: utf-8 -*-

from _ast import slice, Str
from builtins import str, int
from math import ceil, floor
from _operator import rshift
'''
firstArg = [
    {"name":"loginType","value":"2"},
    {"name":"password","value":"123456"}
]
secondArg = ["password"];
thirdArg = {"e": "10001","maxdigits":"67","n":"d3f513f05792e7cea5a8f2d18bb1bb25bce9b88c05433391061aece7e342f3537c9d5da7c901696f7e3c4b6736752a77ac569aa650d1a28acc6f01540bb3fbc1"}
'''

'''
@author: Jacklin
'''
class RSAKeyPair():

    digits = []
    isNeg = False
    ZERO_ARRAY = []
    def BigInt(self,a) :
        global digits,bigOne, bitsPerDigit, biRadix,biHalfRadix,biRadixSquared,maxDigitVal, maxInteger,maxDigits,highBitMasks,lowBitMasks
        self.highBitMasks = [0,32768,49152,57344,61440,63488,64512,65024,65280,65408,65472,65504,65520,65528,65532,65534,65535]
        global lowBitMasks 
        self.lowBitMasks = [0,1,3,7,15,31,63,127,255,511,1023,2047,4095,8191,16383,32767,65535]
        self.biRadix = 1 << 16;
        self.biRadixBits = 16;
        self.bitsPerDigit = 16
        self.biHalfRadix = rshift(self.biRadix , 1)
        self.biRadixSquared = self.biRadix * self.biRadix
        self.maxDigitVal = self.biRadix - 1
        self.maxInteger = 9999999999999998
        self.hexToChar = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
        self.hexatrigesimalToChar = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        
        b = {
            "digits":[],
            "isNeg": False
        }
        if (type(a) == "boolean") and (a == True): #{
            b["digits"] = []
        else:#} else {
            b["digits"] = self.ZERO_ARRAY[0:len(self.ZERO_ARRAY)]
        #}
        b["isNeg"] = False
        
        return b
    
    def biToHex(self,b) :
        a = "";
        d = self.biHighIndex(b);
        for c in range(self.biHighIndex(b),-1,-1):#for (var c = biHighIndex(b); c > -1; --c) {
            a += self.digitToHex(b["digits"][c])
        #}
        return a
    
    def biToString(self,d, f) :
        c = self.BigInt(1)
        c["digits"][0] = f
        e = self.biDivideModulo(d, c)
        a = self.hexatrigesimalToChar[e[1]["digits"][0]]
        while (self.biCompare(e[0], self.bigZero) == 1):# {
            e = self.biDivideModulo(e[0], c);
            digit = e[1]["digits"][0];
            a += self.hexatrigesimalToChar[e[1]["digits"][0]]
        #}
        if d["isNeg"] :
            resultval = "-"
        else:
            resultval = ""
        return resultval + self.reverseStr(a)
    
    def digitToHex(self,c) :
        b = 15;
        a = "";
        for i in range(0,4,1):#for (i = 0; i < 4; ++i) {
            a += self.hexToChar[c & b];
            c = rshift(c, 4)
            #c >>>= 4
        #}
        return self.reverseStr(a)
    
    def reverseStr(self,c) :
        a = "";
        for b in range(len(c)-1,-1,-1):#for (var b = c.length - 1; b > -1; --b) {
            a += c[b]#c.charAt(b)
        #}
        return a
    
    
    def setMaxDigits(self,b) :
        
        maxDigits = b
        for a in range(0,int(maxDigits)):#for (var a = 0; a < ZERO_ARRAY.length; a++) {
            self.ZERO_ARRAY.append(0)
        
        #}
        bigZero = self.BigInt(1);
        bigOne = self.BigInt(1);
        bigOne["digits"][0] = 1
        
    
    def init(self,b, c, a):
        self.e = self.biFromHex(b);
        d = self.biFromHex(c);
        m = self.biFromHex(a);
        self.chunkSize = 2 * self.biHighIndex(m);
        self.radix = 16;
        self.barrett = self.BarrettMu(m)
        
    
    
    def BarrettMu(self,a) :
        self.modulus = self.biCopy(a);
        self.thisk = self.biHighIndex(self.modulus) + 1;
        b = self.BigInt(1);
        b["digits"][2 * self.thisk] = 1;
        self.thismu = self.biDivide(b, self.modulus);
        self.bkplus1 = self.BigInt(1)
        self.bkplus1["digits"][self.thisk + 1] = 1
        self.modulo = self.BarrettMu_modulo;
        self.multiplyMod = self.BarrettMu_multiplyMod;
        self.powMod = self.BarrettMu_powMod

    def BarrettMu_modulo(self,h) :
        g = self.biDivideByRadixPower(h, self.thisk - 1);
        e = self.biMultiply(g, self.thismu);
        d = self.biDivideByRadixPower(e, self.thisk + 1);
        c = self.biModuloByRadixPower(h, self.thisk + 1);
        self.k = self.biMultiply(d, self.modulus);
        b = self.biModuloByRadixPower(self.k, self.thisk + 1);
        a = self.biSubtract(c, b);
        if (a["isNeg"]):# {
            a = self.biAdd(a, self.bkplus1)
        #}
        f = self.biCompare(a, self.modulus) >= 0;
        while (f):# {
            a = self.biSubtract(a, self.modulus)
            f = self.biCompare(a, self.modulus) >= 0
        #}
        return a
    
    def BarrettMu_powMod(self,c, f) :
        b = self.BigInt(1);
        b["digits"][0] = 1;
        d = c;
        e = f;
        while (True):# {
            if ((e["digits"][0] & 1) != 0):# {
                b = self.multiplyMod(b, d)#self.multiplyMod(b, d)
            #}
            e = self.biShiftRight(e, 1);
            if (e["digits"][0] == 0 and self.biHighIndex(e) == 0):# {
                break
            #}
            d = self.multiplyMod(d, d)#self.multiplyMod(d, d)
        #}
        return b
    
    def BarrettMu_multiplyMod(self,a, c) :
        b = self.biMultiply(a, c);
        return self.BarrettMu_modulo(b)#self.modulo(b)
     

    def biMultiply(self,h, g) :
        o = self.BigInt(1);
        b = self.biHighIndex(h);
        m = self.biHighIndex(g);
        #l, a, d = [];
        for e in range(0,m+1,1) : #for (var e = 0; e <= m; ++e) {
            f = 0;
            d = e;
            for j in range(0,b+1,1):#for (j = 0; j <= b; ++j,++d) {
                a = o["digits"][d] + h["digits"][j] * g["digits"][e] + f;
                o["digits"][d] = a & self.maxDigitVal;
                f = rshift(a,self.biRadixBits)#a >>> biRadixBits
                d += 1
            #}
            o["digits"][e + b + 1] = f
        #}
#         o["isNeg"] =  not g["isNeg"]
#         h["isNeg"] = not g["isNeg"]
        return o
    
    def biDivideByRadixPower(self,b, c) :
        a = self.BigInt(1);
        self.arrayCopy(b["digits"], c, a["digits"], 0, len(a["digits"]) - c);
        return a
    
    def biModuloByRadixPower(self,b, c) :
        a = self.BigInt(1);
        self.arrayCopy(b["digits"], 0, a["digits"], 0, c);
        return a
    

    
    def biCopy(self,b) :
        #print("biCopy"+str(len(b["digits"])))
        a = self.BigInt(True);
        a["digits"] = b["digits"]
        a["isNeg"] = b["isNeg"]
        return a
    
    def biShiftLeft(self,b, h) :
        d = floor(h / self.bitsPerDigit);
        a = self.BigInt(1);
        self.arrayCopy(b["digits"], 0, a["digits"], d, len(a["digits"]) - d);
        g = h % self.bitsPerDigit;
        c = self.bitsPerDigit - g;
        for e in range(len(a["digits"]) - 1,-1):#for (var e = a.digits.length - 1, f = e - 1; e > 0; --e, --f) {
            f= e-1;
            a["digits"][e] = ((a["digits"][e] << g) & maxDigitVal) | (rshift((a["digits"][f] & self.highBitMasks[g]), c))
            f -= 1
        #}
        a["digits"][0] = ((a["digits"][0] << g) & self.maxDigitVal);
        a["isNeg"] = b["isNeg"]
        return a
    
    def biShiftRight(self,b, h) :
        c = floor(h / self.bitsPerDigit);
        a = self.BigInt(1);
        self.arrayCopy(b["digits"], c, a["digits"], 0, len(b["digits"]) - c)
        f = h % self.bitsPerDigit;
        g = self.bitsPerDigit - f;
        for d in range(0, len(a["digits"]) - 1,1):#for (var d = 0, e = d + 1; d < len(a["digits"]) - 1; ++d,++e) {
            e = d + 1
            a["digits"][d] = rshift(a["digits"][d],f) | ((a["digits"][e] & self.lowBitMasks[f]) << g)#(a["digits"][d] >>> f) | ((a["digits"][e] & self.lowBitMasks[f]) << g)
            e += 1
        #}
        a["digits"][len(a["digits"]) - 1] = rshift(a["digits"][len(a["digits"]) - 1],f)#a["digits"][len(a["digits"]) - 1] >>>= f;
        a["isNeg"] = b["isNeg"];
        return a
    
    def arrayCopy(self,e, h, c, g, f) :
        a = min(h + f, len(e));
        b = g;
        for d in range(h,a,1):#for (var d = h, b = g; d < a; ++d,++b) {
            c[b] = e[d]
            b += 1
        #}
        
    def biMultiplyByRadixPower(self,b, c) :
        a = self.BigInt(1);
        self.arrayCopy(b["digits"], 0, a["digits"], c, len(a["digits"]) - c);
        return a
    
    def biCompare(self,a, c) :
        if (a["isNeg"] != c["isNeg"]): #{
            return 1 - 2 * int(a["isNeg"])
        #}
        for b in range(len(a["digits"]) - 1,0, -1): #for (var b = a.digits.length - 1; b >= 0; --b) {
            if (a["digits"][b] != c["digits"][b]) :#{
                if (a["isNeg"] == True):# {
                    return 1 - 2 * int(a["digits"][b] > c["digits"][b])
                else:#} else {
                    return 1 - 2 * int(a["digits"][b] < c["digits"][b])
                #}
            #}
        #}
        return a
    
    def biAdd(self,b, g):
        
        if (b["isNeg"] != g["isNeg"]):# {
            g["isNeg"] =  not g["isNeg"];
            a = self.biSubtract(b, g);
            g["isNeg"] = not g["isNeg"]
        else:#} else {
            a = self.BigInt(1);
            f = 0;
            
            for d in range(0,len(b["digits"])):#for (var d = 0; d < b.digits.length; ++d) {
                e = b["digits"][d] + g["digits"][d] + f;
                a["digits"][d] = e & 65535;
                f = int(e >= self.biRadix)
            #}
            a["isNeg"] = b["isNeg"]
        #}
        return a
    
    def biSubtract(self,b, g) :
        
        if (b["isNeg"] != g["isNeg"]):# {
            g["isNeg"] = not g["isNeg"];
            a = self.biAdd(b, g);
            g["isNeg"] = not g["isNeg"]
        else:#} else {
            a = self.BigInt(1);
            f = 0
            e = 0
            
            for d in range(0,len(b["digits"]),1):#for (var d = 0; d < b.digits.length; ++d) {
                f = b["digits"][d] - g["digits"][d] + e;
                a["digits"][d] = f & 65535;
                if (a["digits"][d] < 0):# {
                    a["digits"][d] += self.biRadix
                #}
                e = 0 - int(f < 0)
            #}
            if (e == -1):# {
                e = 0;
                for d in range(0,len(b["digits"]),1):#for (var d = 0; d < b.digits.length; ++d) {
                    f = 0 - a["digits"][d] + e;
                    a["digits"][d] = f & 65535;
                    if (a["digits"][d] < 0):# {
                        a["digits"][d] += self.biRadix
                    #}
                    e = 0 - int(f < 0)
                #}
                a["isNeg"] = not b["isNeg"]
            else:#} else {
                a["isNeg"] = b["isNeg"]
            #}
        #}
        return a
    
    def biMultiplyDigit(self,a, g) :
        result = self.BigInt(1)
        f = self.biHighIndex(a)
        e = 0;
        for b in range(0,f+1,1):#for (var b = 0; b <= f; ++b) {
            d = result["digits"][b] + a["digits"][b] * g + e
            result["digits"][b] = d & self.maxDigitVal
            e = rshift(d,self.biRadixBits)#d >>> biRadixBits
        #}
        result["digits"][1 + f] = e;
        return result
    
    def biDivideModulo(self,g, f) :
        a = self.biNumBits(g);
        e = self.biNumBits(f);
        d = f["isNeg"]
        #print("AAAAAA ::: "+str(a))
        #print("EEEEEEEE ::: "+str(e))
        #o, m = []
        if (a < e) :
            if (g["isNeg"]): 
                o = self.biCopy(bigOne);
                o["isNeg"] = not f["isNeg"]
                g["isNeg"] = False;
                f["isNeg"] = False;
                #m = biSubtract(f, g);
                g["isNeg"] = True;
                f["isNeg"] = d
            else:#} else {
                o = self.BigInt(1);
                m = self.biCopy(g)
            #}
            return True#new Array(o,m)
        #}
        o = self.BigInt(1)
        m = g;
        k = ceil(e / self.bitsPerDigit) - 1;
        h = 0;
        while (f["digits"][k] < self.biHalfRadix): #{
            f = self.biShiftLeft(f, 1);
            ++h;
            ++e;
            k = ceil(e / self.bitsPerDigit) - 1
        #}
        m = self.biShiftLeft(m, h);
        a += h;
        u = ceil(a / self.bitsPerDigit) - 1;
        B = self.biMultiplyByRadixPower(f, u - k);
        while (self.biCompare(m, B) != -1):# {
            ++o["digits"][u - k];
            m = self.biSubtract(m, B)
        #}
        for z in range(u,k,-1):#for (var z = u; z > k; --z) {
            if (z >= len(m["digits"])):
                l = 0
            else:
                l = m["digits"][z];
            if((z - 1 >= len(m["digits"]))):
                A = 0
            else: 
                A = m["digits"][z - 1];
            if (z - 2 >= len(m["digits"])):
                w = 0
            else: 
                w = m["digits"][z - 2];
            if (k >= len(f["digits"])):
                v = 0
            else: 
                v = f["digits"][k]; 
            if (k - 1 >= len(f["digits"])):
                c = 0
            else: 
                c = f["digits"][k - 1]  
                
#             l = (z >= len(m["digits"])) ? 0 : m["digits"][z];
#             A = (z - 1 >= len(m["digits"])) ? 0 : m["digits"][z - 1];
#             w = (z - 2 >= len(m["digits"])) ? 0 : m["digits"][z - 2];
#             v = (k >= len(f["digits"])) ? 0 : f["digits"][k];
#             c = (k - 1 >= len(f["digits"])) ? 0 : f["digits"][k - 1];
            if (l == v) :
                o["digits"][z - k - 1] = self.maxDigitVal
            else:#} else {
                o["digits"][z - k - 1] = floor((l * self.biRadix + A) / v)
            #}
            s = o["digits"][z - k - 1] * ((v * self.biRadix) + c);
            p = (l * self.biRadixSquared) + ((A * self.biRadix) + w);
            while (s > p):# {
                o["digits"][z - k - 1] = o["digits"][z - k - 1] - 1#--o["digits"][z - k - 1];
                s = o["digits"][z - k - 1] * ((v * self.biRadix) | c);
                p = (l * self.biRadix * self.biRadix) + ((A * self.biRadix) + w)
            #}
            B = self.biMultiplyByRadixPower(f, z - k - 1);
            m = self.biSubtract(m, self.biMultiplyDigit(B, o["digits"][z - k - 1]));
            if (m["isNeg"]):# {
                m = self.biAdd(m, B);
                o["digits"][z - k - 1] = o["digits"][z - k - 1] - 1#--o["digits"][z - k - 1]
            #}
        #}
        m = self.biShiftRight(m, h);
        o["isNeg"] = g["isNeg"] != d;
        if (g["isNeg"]): #{
            if (d) :#{
                o = self.biAdd(o, self.bigOne)
            else:#} else {
                o = self.biSubtract(o, self.bigOne)
            #}
            f = self.biShiftRight(f, h);
            m = self.biSubtract(f, m)
        #}
        if (m["digits"][0] == 0 and self.biHighIndex(m) == 0):# {
            m["isNeg"] = False
        #}
        resultArr = [o,m]
        #print("resultArr:: "+str(len(o["digits"]))+" MM "+str(len(m["digits"])))
        return resultArr#new Array(o,m)
    
    def biNumBits(self,c) :
        bitsPerDigit = 16;
        f = self.biHighIndex(c);
        e = c["digits"][f];
        b = (f + 1) * bitsPerDigit;
        for a in range(b,b - bitsPerDigit,-1): #(a = b; a > b - bitsPerDigit; --a) {
            if ((e & 32768) != 0):# {
                break
            #}
            e <<= 1
        #}
        return a
    
    def biDivide(self,a, b) :
        return self.biDivideModulo(a, b)[0]
    
    def biModulo(self,a, b) :
        return self.biDivideModulo(a, b)[1]
#     
    
    def biHighIndex(self,b) :
        a = len(b["digits"]) - 1;
        #print("biHighIndex:: "+str(a))
        while (a > 0 and b["digits"][a] == 0):# {
            a -= 1
        #}
        ###print("biHighIndex:: "+str(a))
        return a  
      
    def charToHex(self,k) :
        d = 48;
        b = d + 9;
        e = 97;
        h = e + 25;
        g = 65;
        f = 65 + 25;
        a = 0
        if (k >= d and k <= b): #{
            a = k - d
        else:#} else {
            if (k >= g and k <= f) :#{
                a = 10 + k - g
            else:#} else {
                if (k >= e and k <= h):# {
                    a = 10 + k - e
                else:#} else {
                    a = 0
                #}
            #}
        #}
        
        return a
    
    def hexToDigit(self,d) :
        
        b = 0;
        a = min(len(d), 4);
        ###print("DDDDD:: "+str(d))
        ###print(a)
        for c in range(0,a):#for (var c = 0; c < a; ++c) {
            b = b * (4*4)#b <<= 4;
            b |= self.charToHex(ord(d[c]))#b |= self.charToHex(ord(d[c]))
        #}
        ###print("charToHex::: "+str(b))
        return b
    
    def biFromHex(self,e):
        b = self.BigInt(1)
        a = len(e);
        c = 0;
        for d in range(a,0,-4):
            if  d > 0:
                if d - 4 < 0:
                    value = e[0: (min(d, 4))]
                else:
                    value = e[max(d - 4, 0): (max(d - 4, 0) + 4)]
                b["digits"][c] = self.hexToDigit(value)
                c += 1
        return b
      

def encryptedString(l, o) :
        h = []
        b = len(o)
        f = 0
        while (f < b):
            h.append(ord(o[f]))#o.charCodeAt(f);
            f += 1
        
        while (len(h) % l.chunkSize != 0) :
            h.append(0)#h[f] = 0
            f += 1
        
        g = len(h);
        p = "";
        # var e, d, c;
        for f in range(0,g, l.chunkSize):#for (f = 0; f < g; f += l.chunkSize) {
            if f < g:
                c = l.BigInt(1);
                e = 0;
                d = f
                for dd in range(f,f + l.chunkSize,2):#for (d = f; d < f + l.chunkSize; ++e) {
                    c["digits"][e] = h[d];
                    d += 1
                    c["digits"][e] += h[d] << 8
                    d += 1
                    e += 1
                
                n = l.BarrettMu_powMod(c, l.e)
                #m = l.radix == 16 ? biToHex(n) : biToString(n, l.radix);
                if l.radix == 16 :
                    m = l.biToHex(n)
                else:
                    m = l.biToString(n, l.radix)
                p += m + " "
                
        
        return p[0:len(p)- 1]#p.substring(0, p.length - 1)
    

def encryptForm(a, c) :
    h = c["maxdigits"]
    f = c["e"];
    k = c["n"];
    
    b =  RSAKeyPair()
    b.setMaxDigits(h)
    b.init(f,"",k)
    #value = str(a[1]["value"])
    value = str(a)
    encValue = encryptedString(b, value)
    print("ENCRYPT::: "+encValue)

    return encValue

#encryptForm(firstArg,secondArg,thirdArg)