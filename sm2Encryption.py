# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 10:02:25 2017

@author: Administrator
"""
'''
import time
import math
from _operator import rshift
import random
class RSAKey():
    
    def __init__(self):
        self.n = None;
        self.e = 0;
        d = None;
        p = None;
        q = None;
        dmp1 = None;
        dmq1 = None;
        coeff = None;
        rng_state = None
        rng_pool = None
        rng_pptr = None
        this = []
        BI_RC = []
    
    
    def setPublic(self, N,E):
        self.BI_RC = []
        self.this = []
        if(N != None and E != None and len(N) > 0 and len(E) > 0):
            self.n = self.parseBigInt(N,16);
            self.e = int(E,16);
            #print(self.n.this)
            #print("end public")
        else:
            print("Invalid RSA public key");
            
    def parseBigInt(self, str,r):
        
        return BigInteger(str, r)
    
    def encrypt(self, text):
        m = self.pkcs1pad2(text, (self.n.bitLength()+7)>>3);
        
        if(m == None):
            return None;
        c = self.doPublic(m)
       
        if(c == None):
            return None;
        #print(c)
        h = c.toString(16);
        i = 256 - len(h);
        #for (var s = 0; s < i; s += 1)
        for s in range ( 0, i , 1):
            h = "0" + h;
        return h

          
        
    def doPublic(self, x):
        
        return x.modPowInt(self.e, self.n);
        
    
    def pkcs1pad2(self, s, n):
        if(n < len(s) + 2):
            print("Message too long for RSA");
            return null;
        
        ba = [None] * 128
        i = len(s) - 1
        ii = len(s)
        if (ii < 100):
            ba[0] = 48 + ii / 10
            ba[1] = 48 + ii % 10
            ss = 2
            i = 0
            while (i < ii and n > 0):
                
                ba[ss] = ord(s[i])#s[i+1]
                i = i + 1
                ss = ss + 1
                #print(ba)
                
            u = SecureRandom()
            a = [None] * 2
            while (ss < n):
                a[0] = 0
                while (a[0] == 0):
                    u.nextBytes(a)
                ba[ss] = a[0]
                ss = ss+1
            #print(ba)
            return BigInteger(ba);  
        
    
class Arcfour():
    
    def __init__(self):
        self.thisi = 0
        self.thisj = 0
        self.thisS = [None] * 256
        
        

    def init(self, key):
        i = 0
        j = 0
        t = 0
        for i in range(256):
            self.thisS[i] = i;
        j = 0;
        for i in range(256):
            j = (j + self.thisS[i] + key[i % len(key)]) & 255;
            t = self.thisS[i];
            self.thisS[i] = self.thisS[j];
            self.thisS[j] = t;
        
        self.thisi = 0;
        self.thisj = 0;


    def next(self):
        t = None
        self.thisi = (self.thisi + 1) & 255;
        self.thisj = (self.thisj + self.thisS[self.thisi]) & 255;
        t = self.thisS[self.thisi];
        self.thisS[self.thisi] = self.thisS[self.thisj];
        self.thisS[self.thisj] = t;
        return self.thisS[(t + self.thisS[self.thisi]) & 255];


def prng_newstate():
    return Arcfour()
    
    
def nbi(): 
    return BigInteger(None)
   

class BigInteger():
    this = []
    def __init__(self, a = None, b = None, c = None):
        self.t = 0
        self.s = 0   
        self.DB = 0
        self.BI_RC = [None] * 123
        self.DM = 0
        self.this = [None] * 128
        
        dbits = 28
        
        self.DB = dbits
        self.DM = ((1<<dbits)-1)
        self.DV = (1<<dbits)
        
        self.BI_FP = 52
        self.FV = math.pow(2, self.BI_FP)
        self.F1 = self.BI_FP - dbits
        self.F2 = 2 * dbits - self.BI_FP
        
        # Digit conversions
        self.BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz";
        rr = 0
        vv = 0
        #rr = "0".charCodeAt(0);
        rr = ord("0"[0])
        #print(rr)
        for vv in range(0, 10, 1):
            self.BI_RC[rr] = vv;
            rr = rr+1
            
        #print(self.BI_RC)
        #rr = "a".charCodeAt(0);
        rr = ord("a"[0])
        #print(rr)
        #for(vv = 10; vv < 36; ++vv) BI_RC[rr++] = vv;
        for vv in range(10, 36, 1):
            #print("inside :  "+str(rr))
            self.BI_RC[rr] = vv;
            rr = rr+1
            
        #print(self.BI_RC)
        #rr = "A".charCodeAt(0);
        rr = ord("A"[0])
        #print(rr)
        #for(vv = 10; vv < 36; ++vv) BI_RC[rr++] = vv;
        for vv in range(10, 36, 1):
            self.BI_RC[rr] = vv;
            rr = rr+1
        #print(self.BI_RC)
        
        if(a != None):
            if(int == type( a) ):
                #fromNumber(a,b,c);
                print("fromnumber")
            elif(b == None and str != type(a)):
                self.fromString(a,256);
            else: 
                self.fromString(a,b);
        
    
    def ONE(self):
        return self.nbv(1)
    
    def ZERO(self):
        return self.nbv(0)
        
    def nbv(self, i):
        r = nbi()
        r.fromInt(i)
        return r
    
    def squareTo(self, r):
        x = self.abs()
         
        r.t = 2*x.t
        i = r.t
        i = i - 1
        while(i >= 0):
            r.this[i] = 0;
            i = i - 1
        #for(i = 0; i < x.t-1; ++i) {
        for i in range(0, x.t-1, 1):
            c = x.am(i,x.this[i],r,2*i,0,1)
            r.this[i + x.t] += x.am(i+1,2*x.this[i],r,2*i+1,c,x.t-i-1)
            if( r.this[i + x.t] >= x.DV):
                r[i+x.t] -= x.DV;
                r[i+x.t+1] = 1;
            i = i
        i = i + 1
#         print(i)
        if(r.t > 0):
            r.this[r.t-1] += x.am(i,x.this[i],r,2*i,0,1)
        r.s = 0;
        r.clamp();
       
    def multiplyTo(self, a,r):
        x = self.abs()
        y = a.abs()
        i = x.t
        r.t = i+y.t
        i = i - 1
        while(i >= 0):
            r.this[i] = 0
            i = i - 1
        #for(i = 0; i < y.t; ++i)
        for i in range( 0, y.t , 1):
            r.this[i+x.t] = x.am(0,y.this[i],r,i,0,x.t);
        r.s = 0;
        r.clamp();
        if(self.s != a.s):
            zero = BigInteger.ZERO
            zero.subTo(r,r);
        
    
    def am(self, i,x,w,j,c,n):
        xl = x&0x3fff
        xh = x>>14
        
        while(n >= 0):
            n = n - 1
            if( n != -1):
                l = self.this[i]&0x3fff
                h = self.this[i] >> 14
                i = i + 1
                m = xh*l+h*xl
                if(j == -1):
                    l = 0
                else:
                    l = xl*l+((m&0x3fff)<<14)+w.this[j]+c
                c = (l>>28)+(m>>14)+xh*h
                w.this[j] = l&0xfffffff
                j = j + 1
            
          
        
        return c;
        
    def toString(self, b):
        if(self.s < 0):
            return "-"+ self.negate().toString(b);
        k = None
        if(b == 16):
            k = 4
        elif(b == 8):
            k = 3;
        elif(b == 2):
            k = 1;
        elif(b == 32):
            k = 5;
        elif(b == 4):
            k = 2;
        else:
            return self.toRadix(b);
        km = (1<<k)-1
        d = None
        m = False
        r = ""
        i = self.t
        p = self.DB-(i*self.DB)%k;
        #i = i -1
        if(i > 0):
            i = i -1
            d = self.this[i]>>p
            if(p < self.DB and (d) > 0):
                m = True
                r = self.int2char(d)
            while(i >= 0):
                if(p < k): 
                    d = (self.this[i]&((1<<p)-1))<<(k-p);
                    
                    p = p + self.DB-k
                    d |= self.this[i]>>(p)
                    i = i -1
                else:
                    p = p - k
                    d = (self.this[i]>>(p))&km
                    if(p <= 0):
                        p += self.DB; 
                        i = i - 1
                
                if(d > 0):
                    m = True
                if(m):
                    r += self.int2char(d)
          
        if(m):
            returnstr = r
        else:
            returnstr = "0"
        return returnstr
        
    def int2char(self, n):
        return self.BI_RM[n]
       
    def intAt(self,s,i):
        #print(s)
        #print(i)
        #print(s[i])
        #print(ord(s[i]))
        c = self.BI_RC[ord(s[i])]
        #print(c)
        if(c == None):
            returnval = -1
        else:
            returnval = c
        return returnval
    
    
    
    def fromString(self,ss,b):
        k = 0
        #print(self.this)
        #print(self.BI_RC)
        
        if(b == 16):
            k = 4
        elif(b == 8): 
            k = 3
        elif(b == 256): 
            k = 8
        elif(b == 2): 
            k = 1
        elif(b == 32): 
            k = 5
        elif(b == 4): 
            k = 2
        else:
            print("fromRadix(s,b)")
            return
        self.t = 0;
        self.s = 0;
        i = len(ss)
        mi = False
        sh = 0;
        self.this = [None] * i
        
        while(i > 0):
            #print(i)
            i = i - 1
            #x = (k==8)?s[i]&0xff:intAt(s,i);
            x = 0
            if(k==8):
                if(type(ss[i]) is int):
                    x = ss[i]&0xff
                else:
                    ss[i] = int(ss[i])
                    x = ss[i]&0xff
            else:
                x = self.intAt(ss,i)
            
            if(x < 0):
                if(ss[i] == "-"):
                    mi = True;
                continue;
            
            mi = False;
            if(sh == 0):
                self.this[self.t] = x
                self.t = self.t+1
            elif(( sh + k ) > self.DB):
                
                self.this[self.t-1] |= (x & ( ( 1 << (self.DB-sh) ) -1) ) << sh
                self.this[self.t] = (x >> ( self.DB - sh ))
                self.t = self.t + 1
            
            else:
                self.this[self.t-1] |= x << sh
            sh += k
            if(sh >= self.DB):
                sh -= self.DB
            
#         print(ss[0])
        #if(k == 8 and (ss[0]&0x80) != 0):
        if(k == 8 and (int(ss[0]) &0x80) != 0):
            self.s = -1;
            if(sh > 0):
                
                self.this[self.t - 1] |= ((1<<(self.DB-sh))-1)<<sh
        
        self.clamp()
        if(mi):
            BigInteger.ZERO.subTo(self.this,self.this);
            
    def clamp(self):
        c = self.s & self.DM
        while(self.t > 0 and self.this[self.t-1] == c):
            self.t = self.t - 1;
            
    
        
    def bitLength(self):
        if(self.t <= 0):
            return 0;
        return self.DB * (self.t-1) + self.nbits( self.this[self.t-1] ^ ( self.s & self.DM) )
        
    def nbits(self,x):
        r = 1
        t = rshift(x, 16)#x >>>16
        if((t) != 0):
            x = t;
            r += 16;
        t = x>>8
        if(t != 0):
            x = t; 
            r += 8; 
        t=x>>4
        if(t != 0):
            x = t; 
            r += 4;
        t = x>>2
        if((t) != 0):
            x = t; 
            r += 2; 
        t=x>>1
        if(t != 0):
            x = t; 
            r += 1; 
        return r;
            
    def modPowInt(self,e,m):
        z = None
        
        if(e < 256 or m.isEven()):
            z = Classic(m)
        else:
            z = Montgomery(m);
        return self.exp1(e,z);
    
    def nbv(self,i):
        r = nbi(); 
        r.fromInt(i); 
        return r; 
    
    
    
    def exp1(self,e,z) :
        if(e > 0xffffffff or e < 1):
            return  BigInteger.ONE(self)
        r = nbi()
        #print("RRRRRRRr")
        #print(r.this)
        r2 = nbi()
        #print("RRRRRRR32222222")
        #print(r2.this)
        g = z.convert(self)
        i = self.nbits(e)-1;
        g.copyTo(r);
        #print("AFTER  RRRRRRRr")
        #print(r.this)
        
#         print("EXP1")
        #print(self.this)
#         print(i)
        while(i > 0):
            i = i -1
#             print("inside while ")
#             print(i)
            z.sqrTo(r,r2);
            if((e&(1<<i)) > 0):
                z.mulTo(r2,g,r);
            else:
                t = r; 
                r = r2; 
                r2 = t;
        
        return z.revert(r);
        

    
            
    def isEven(self):
        returnVal  = None
        if(self.t>0):
            val = (self.this[0]&1)
        else: 
            val = self.s
        
        returnVal = (val == 0)
        return returnVal
    
    def invDigit(self):
        if(self.t < 1):
            return 0;
        x = self.this[0];
        if((x&1) == 0):
            return 0;
        y = x&3
        y = (y*(2-(x&0xf)*y))&0xf
        y = (y*(2-(x&0xff)*y))&0xff
        y = (y*(2-(((x&0xffff)*y)&0xffff)))&0xffff
        y = (y*(2-x*y%self.DV))% self.DV
        returnval = None
        if( y>0):
            returnval = self.DV -y
        else:
            returnval = -y
        return returnval
    
    def compareTo(self, a):
        r = self.s - a.s;
        if(r != 0):
            return r
        i = self.t
        r = i - a.t
        if(r != 0):
            returnval = None
            if (s < 0):
                returnval = -r
            else:
                returnval = r
            return returnval
        
        while(i >= 0):
            i = i - 1
            r=self.this[i]-a.this[i]
            if(r != 0):
                return r;
            #i = i - 1
        return 0;
    
    def mod(self, a):
        r = nbi();
        abs().divRemTo(a,null,r);
        if(s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            a.subTo(r,r);
        return r;
    
    def copyTo(self, r):
        #for(i = this.t-1; i >= 0; --i):
        for i in range(self.t-1, -1,-1):
            r.this[i] = self.this[i];
        r.t = self.t;
        r.s = self.s;
        
    
    def fromInt(self, x):
        self.t = 1;
        if (x<0):
            self.s = -1
        else:
            self.s= 0
        if(x > 0):
            self.this[0] = x
        elif(x < -1):
            self.this[0] = x + self.DV
        else: 
            self.t = 0
        
    def lShiftTo(self, n,r):
        bs = n%self.DB
        cbs = self.DB-bs
        bm = (1<<cbs) -1
        ds = math.floor( n/self.DB)
        c = (self.s<<bs) & self.DM
        i = 0
        
#        for(i = this.t-1; i >= 0; --i) {
        #i = self.t-1
        #while(i >= 0):
        for i in range(self.t-1, -1, -1):
            if(self.this[i] != None):
                r.this[i+ds+1] = (self.this[i]>>cbs)|c
                c = (self.this[i]&bm)<<bs
            
        
        #for(i = ds-1; i >= 0; --i) r[i] = 0;
        i = ds-1
        for i in range(ds-1,  -1, -1):
            r.this[i] = 0;
        r.this[ds] = c;
        r.t = self.t+ds+1;
        r.s = self.s;
        r.clamp();
        #i = i - 1

    

            
    def rShiftTo(self, n,r):
        r.s = self.s;
        ds = math.floor(n/ self.DB);
        if(ds >= self.t):
            r.t = 0
            return
        bs = n%self.DB;
        cbs = self.DB-bs
        bm = (1<<bs)-1
        r.this[0] = self.this[ds]>>bs
#         for(var i = ds+1; i < this.t; ++i) {
        for i in range(ds+1, self.t, 1):
            r.this[i-ds-1] |= (self.this[i]&bm)<<cbs
            r.this[i-ds] = self.this[i]>>bs
        
        if(bs > 0):
            r.this[self.t-ds-1] |= (self.s&bm)<<cbs
        r.t = self.t-ds
        r.clamp()
        
        
    def dlShiftTo(self, n,r):
        #print(len(self.this))
#         for(i = this.t-1; i >= 0; --i) r[i+n] = this[i];
        for i in range(self.t-1, -1 , -1):
            r.this[i+n] = self.this[i]
#         for(i = n-1; i >= 0; --i) r[i] = 0;
        for i in range(n-1, -1, -1):
            r.this[i] = 0
        r.t = self.t+n;
        r.s = self.s;
    
    def drShiftTo(self, n,r):
#         for(var i = n; i < this.t; ++i) r[i-n] = this[i];
        for i in range(n, self.t, 1):
            r.this[i-n] = self.this[i]
            
        r.t = max(self.t-n,0);
        r.s = self.s;
        

        
    def subTo(self, a,r):
        i = 0
        c = 0
        m = min(a.t,self.t)
        while(i < m):
            #print(i)
            #print(self.this[i])
            #print(a.this[i])
            c = c +  self.this[i]-a.this[i]
            r.this[i] = c&self.DM;
            i = i+1
            c >>= self. DB;
        
        if(a.t < self.t):
            c -= a.s;
            while(i < self.t):
                c += self.this[i];
                r.this[i] = c&self.DM;
                c >>= self.DB;
                i = i+1
          
            c += self.s;
        
        else:
            c += self.s;
            while(i < a.t):
                c -= a.this[i]
                r.this[i] = c&self.DM
                c >>= self.DB
                i = i+1
          
            c -= a.s
        
#         r.s = (c<0)?-1:0;
        if (c<0) :
            r.s = -1
        else:
            r.s = 0
        if(c < -1):
            r.this[i] = self.DV+c
            i = i+1
        elif(c > 0):
            r.this[i] = c
            i = i+1
        r.t = i
        r.clamp()
        

    
    def divRemTo(self, m,q,r):
        pm = m.abs()
        if(pm.t <= 0):
            return
        pt = self.abs()
        if(pt.t < pm.t):
            if(q != None):
                q.fromInt(0);
            if(r != None):
                self.copyTo(r);
            return;
        
        if(r == None):
            r = nbi()
        y = nbi()
        ts = self.s
        ms = m.s
        nsh = self.DB - self.nbits(pm.this[pm.t-1])
        if(nsh > 0):
            pm.lShiftTo(nsh,y) 
            pt.lShiftTo(nsh,r)
        else:
            pm.copyTo(y)
            pt.copyTo(r); 
        ys = y.t
        y0 = y.this[ys-1]
        if(y0 == 0):
            return;
#         yt = y0*(1<<this.F1)+((ys>1)?y[ys-2]>>this.F2:0)
        if(ys>1):
            val = y.this[ys-2]>>self.F2
        else: 
            val = 0
        #print("1")
        #print(self.this)
        yt =  y0*(1<<self.F1) + val
        d1 = self.FV/yt
        d2 = (1<<self.F1)/yt
        e = 1<<self.F2;
        i = r.t
        j = i-ys
        #print("2")
        #print(self.this)
#         t = (q==null)?nbi():q;
        if (q==None):
            t = nbi()
        else:
            t = q
        y.dlShiftTo(j,t)
        #print("3")
        #print(self.this)
        if(r.compareTo(t) >= 0):
            r.this[r.t] = 1
            r.t = r.t+1
            r.subTo(t,r);
        one = BigInteger.ONE(self)
        #print("4")
        #print(self.this)
        one.dlShiftTo(ys,t);
        #print("5")
        #print(self.this)
        t.subTo(y,y);    
        while(y.t < ys):
            y.this[y.t] = 0
            y.t = y.t+1
        
        while(j >= 0):
            j = j -1
            if( j != -1):
                #if(j != -1):
        #             qd = (r[--i]==y0)?this.DM:Math.floor(r[i]*d1+(r[i-1]+e)*d2);
        
                ifcop = r.this[i]
                i = i - 1
                if  (ifcop ==y0) :
                    qd = self.DM
                else:
                    qd = math.floor(r.this[i]*d1+(r.this[i-1]+e)*d2)
                    
                r.this[i] = r.this[i] + y.am(0,qd,r,j,0,ys)
                if((r.this[i]) < qd):
                    y.dlShiftTo(j,t);
                    r.subTo(t,r);
                    #qd = qd - 1
                    while(r.this[i] < qd):
                        qd = qd - 1
                        r.subTo(t,r);
                    
            
        if(q != None):
            r.drShiftTo(ys,q);
            if(ts != ms):
                BigInteger.ZERO.subTo(q,q);
        
        r.t = ys;
        r.clamp();
        if(nsh > 0):
            r.rShiftTo(nsh,r)
        if(ts < 0):
            BigInteger.ZERO.subTo(r,r);
        

        
        
    def abs(self):
        returnVal = None
        if (self.s<0):
            returnVal = self.negate()
        else:
            returnVal = self
        return returnVal
    
    def negate(self):
        r = nbi()
        BigInteger.ZERO.subTo(this,r)
        return r
        
        
m = None
class Classic():
    def __init__(self, m):
        thism = m
    def convert(self, x):
        if(x.s < 0 or x.compareTo(thism) >= 0):
            return x.mod(thism);
        else:
            return x;
    
m = None    
class  Montgomery():
    def __init__(self, m):
        self.thism = m;
        self.thismp = m.invDigit();
        self.thismpl = self.thismp&0x7fff;
        self.thismph = self.thismp>>15;
        self.thisum = (1<<(m.DB-15))-1;
        self.thismt2 = 2*m.t;
    
    def convert(self, x):
        r = nbi()
        x.abs().dlShiftTo(self.thism.t,r)
        r.divRemTo(self.thism,None,r);
        if(x.s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            self.thism.subTo(r,r)
        return r
    
    def reduce(self, x):
        while(x.t <= self.thismt2):
            x.this[x.t] = 0
            x.t = x.t + 1
        #for(var i = 0; i < this.m.t; ++i) {
        i = 0
        for  i in range( 0, self.thism.t, 1):
            j = x.this[i]&0x7fff;
            u0 = (j*self.thismpl+(((j*self.thismph+(x.this[i]>>15)*self.thismpl)&self.thisum)<<15))&x.DM;
            j = i+self.thism.t;
            x.this[j] += self.thism.am(0,u0,x,i,0,self.thism.t);
          
            while(x.this[j] >= x.DV):
                x.this[j] = x.this[j] - x.DV; 
                j = j + 1
                x.this[j] = x.this[j] + 1
        
        x.clamp();
        x.drShiftTo(self.thism.t,x);
        if(x.compareTo(self.thism) >= 0):
            x.subTo(this.m,x);
        

    
    def sqrTo(self, x,r):
        x.squareTo(r)
        self.reduce(r)
        
    def mulTo(self, x,y,r):
        x.multiplyTo(y,r)
        self.reduce(r)
        
    def revert(self, x):
        r = nbi()
        x.copyTo(r);
        self.reduce(r);
        return r;
        
    

class SecureRandom():
    
    def __init__(self):
        self.rng_state = None
        self.rng_pool = None
        self.rng_ppt = None
        self.rng_psize = 256
        if(self.rng_pool == None):
            self.rng_pool = [None] * 256
            self.rng_pptr = 0;
            
            while(self.rng_pptr < self.rng_psize):
                t = math.floor(65536 * random.random())
                #t = math.floor(65536 * 2)
                self.rng_pool[self.rng_pptr] = rshift(t, 8)#t >>> 8
                self.rng_pptr = self.rng_pptr + 1
                
                self.rng_pool[self.rng_pptr] = t & 255
                self.rng_pptr = self.rng_pptr + 1
            
            self.rng_pptr = 0;
            self.rng_seed_time();

            
    
    def rng_get_byte(self):
        if(self.rng_state == None):
            self.rng_seed_time();
            self.rng_state = prng_newstate()
            self.rng_state.init(self.rng_pool)
            #for(rng_pptr = 0; rng_pptr < rng_pool.length; ++rng_pptr)
            rng_pptr = 0
            for rng_pptr in range(0, len(self.rng_pool), 1):
                self.rng_pool[rng_pptr] = 0;
            self.rng_pptr = 0;
          
        return self.rng_state.next();
    
    
    def nextBytes(self, ba):
        i = 0
        lencount = 0
        for jj in range( len(ba) ):
            if(ba[jj] != None):
                lencount = lencount + 1
        for i in range( 0 , lencount, 1):# (i = 0; i < ba.length; ++i):
            ba[i] = self.rng_get_byte()
            
    
    def rng_seed_int(self, x) :
        self.rng_pool[self.rng_pptr] ^= x & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 8) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 16) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 24) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        if(self.rng_pptr >= self.rng_psize):
            self.rng_pptr = self.rng_pptr - self.rng_psize
        
    
    def rng_seed_time(self):
        self.rng_seed_int(round(time.time() * 1000))
        #self.rng_seed_int(1498555878795)
    
    
'''

import time
import math
from _operator import rshift
import random
class RSAKey():
    
    def __init__(self):
        self.n = None;
        self.e = 0;
        d = None;
        p = None;
        q = None;
        dmp1 = None;
        dmq1 = None;
        coeff = None;
        rng_state = None
        rng_pool = None
        rng_pptr = None
        this = []
        BI_RC = []
    
    
    def setPublic(self, N,E):
        self.BI_RC = []
        self.this = []
        if(N != None and E != None and len(N) > 0 and len(E) > 0):
            self.n = self.parseBigInt(N,16);
            self.e = int(E,16);
            #print(self.n.this)
            #print("end public")
        else:
            print("Invalid RSA public key");
            
    def parseBigInt(self, str,r):
        
        return BigInteger(str, r)
    
    def encrypt(self, text):
        m = self.pkcs1pad2(text, (self.n.bitLength()+7)>>3);
        '''print("Encrypt MMMM :: ")
        print(m.this)
        print(m.t)'''
        if(m == None):
            return None;
        c = self.doPublic(m)
        '''print("ccccc")
        print(c.this)
        print(c.t)'''
        if(c == None):
            return None;
        #print(c)
        h = c.toString(16);
        i = 256 - len(h);
        #for (var s = 0; s < i; s += 1)
        for s in range ( 0, i , 1):
            h = "0" + h;
        return h

          
        
    def doPublic(self, x):
        '''print("SELF.N XXXXX ")
        print(self.n.this)
        print("doPublic XXXXX ")
        print(x.this)
        print(x.t)'''
        return x.modPowInt(self.e, self.n);
        
    
    def pkcs1pad2(self, s, n):
        if(n < len(s) + 2):
            print("Message too long for RSA");
            return None;
        
        ba = [None] * 128
        i = len(s) - 1
        ii = len(s)
        if (ii < 100):
            ba[0] = 48 + ii / 10
            ba[1] = 48 + ii % 10
            ss = 2
            i = 0
            while (i < ii and n > 0):
                
                ba[ss] = ord(s[i])#s[i+1]
                i = i + 1
                ss = ss + 1
                #print(ba)
                
            u = SecureRandom()
            a = [None] * 2
            while (ss < n):
                a[0] = 0
                while (a[0] == 0):
                    u.nextBytes(a)
                ba[ss] = a[0]
                ss = ss+1
            #print(ba)
            return BigInteger(ba);  
        
    
class Arcfour():
    
    def __init__(self):
        self.thisi = 0
        self.thisj = 0
        self.thisS = [None] * 256
        
        

    def init(self, key):
        i = 0
        j = 0
        t = 0
        for i in range(256):
            self.thisS[i] = i;
        j = 0;
        for i in range(256):
            j = (j + self.thisS[i] + key[i % len(key)]) & 255;
            t = self.thisS[i];
            self.thisS[i] = self.thisS[j];
            self.thisS[j] = t;
        
        self.thisi = 0;
        self.thisj = 0;


    def next(self):
        t = None
        self.thisi = (self.thisi + 1) & 255;
        self.thisj = (self.thisj + self.thisS[self.thisi]) & 255;
        t = self.thisS[self.thisi];
        self.thisS[self.thisi] = self.thisS[self.thisj];
        self.thisS[self.thisj] = t;
        return self.thisS[(t + self.thisS[self.thisi]) & 255];


def prng_newstate():
    return Arcfour()
    
    
def nbi(): 
    return BigInteger(None)
   

class BigInteger():
    this = []
    def __init__(self, a = None, b = None, c = None):
        self.t = 0
        self.s = 0   
        self.DB = 0
        self.BI_RC = [None] * 123
        self.DM = 0
        self.this = [None] * 128
        
        dbits = 28
        
        self.DB = dbits
        self.DM = ((1<<dbits)-1)
        self.DV = (1<<dbits)
        
        self.BI_FP = 52
        self.FV = math.pow(2, self.BI_FP)
        self.F1 = self.BI_FP - dbits
        self.F2 = 2 * dbits - self.BI_FP
        
        # Digit conversions
        self.BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz";
        rr = 0
        vv = 0
        #rr = "0".charCodeAt(0);
        rr = ord("0"[0])
        #print(rr)
        for vv in range(0, 10, 1):
            self.BI_RC[rr] = vv;
            rr = rr+1
            
        #print(self.BI_RC)
        #rr = "a".charCodeAt(0);
        rr = ord("a"[0])
        #print(rr)
        #for(vv = 10; vv < 36; ++vv) BI_RC[rr++] = vv;
        for vv in range(10, 36, 1):
            #print("inside :  "+str(rr))
            self.BI_RC[rr] = vv;
            rr = rr+1
            
        #print(self.BI_RC)
        #rr = "A".charCodeAt(0);
        rr = ord("A"[0])
        #print(rr)
        #for(vv = 10; vv < 36; ++vv) BI_RC[rr++] = vv;
        for vv in range(10, 36, 1):
            self.BI_RC[rr] = vv;
            rr = rr+1
        #print(self.BI_RC)
        
        if(a != None):
            if(int == type( a) ):
                #fromNumber(a,b,c);
                print("fromnumber")
            elif(b == None and str != type(a)):
                self.fromString(a,256);
            else: 
                self.fromString(a,b);
        
    
    def ONE(self):
        return self.nbv(1)
    
    def ZERO(self):
        return self.nbv(0)
        
    def nbv(self, i):
        r = nbi()
        r.fromInt(i)
        return r
   
    
    def squareTo(self, r):
        x = self.abs()
         
        r.t = 2*x.t
        i = r.t
        i = i - 1
        while(i >= 0):
            r.this[i] = 0;
            i = i - 1
        #for(i = 0; i < x.t-1; ++i) {
        for i in range(0, x.t-1, 1):
            c = x.am(i,x.this[i],r,2*i,0,1)
            r.this[i + x.t] += x.am(i+1,2*x.this[i],r,2*i+1,c,x.t-i-1)
            if( r.this[i + x.t] >= x.DV):
                r[i+x.t] -= x.DV;
                r[i+x.t+1] = 1;
            i = i
        i = i + 1
#         print(i)
        if(r.t > 0):
            r.this[r.t-1] += x.am(i,x.this[i],r,2*i,0,1)
        r.s = 0;
        r.clamp();
       
    def multiplyTo(self, a,r):
        x = self.abs()
        y = a.abs()
        i = x.t
        r.t = i+y.t
        i = i - 1
        while(i >= 0):
            r.this[i] = 0
            i = i - 1
        #for(i = 0; i < y.t; ++i)
        for i in range( 0, y.t , 1):
            r.this[i+x.t] = x.am(0,y.this[i],r,i,0,x.t);
        r.s = 0;
        r.clamp();
        if(self.s != a.s):
            zero = BigInteger.ZERO
            zero.subTo(r,r);
        
    
    def am(self, i,x,w,j,c,n):
        xl = x&0x3fff
        xh = x>>14
        
        while(n >= 0):
            n = n - 1
            if( n != -1):
                l = self.this[i]&0x3fff
                h = self.this[i] >> 14
                i = i + 1
                m = xh*l+h*xl
                if(j == -1):
                    l = 0
                else:
                    l = xl*l+((m&0x3fff)<<14)+w.this[j]+c
                c = (l>>28)+(m>>14)+xh*h
                w.this[j] = l&0xfffffff
                j = j + 1
            
          
        
        return c;
        
    def toString(self, b):
        if(self.s < 0):
            return "-"+ self.negate().toString(b);
        k = None
        if(b == 16):
            k = 4
        elif(b == 8):
            k = 3;
        elif(b == 2):
            k = 1;
        elif(b == 32):
            k = 5;
        elif(b == 4):
            k = 2;
        else:
            return self.toRadix(b);
        km = (1<<k)-1
        d = None
        m = False
        r = ""
        i = self.t
        p = self.DB-(i*self.DB)%k;
        #i = i -1
        if(i > 0):
            i = i -1
            d = self.this[i]>>p
            if(p < self.DB and (d) > 0):
                m = True
                r = self.int2char(d)
            while(i >= 0):
                if(p < k): 
                    d = (self.this[i]&((1<<p)-1))<<(k-p);
                    
                    p = p + self.DB-k
                    d |= self.this[i]>>(p)
                    i = i -1
                else:
                    p = p - k
                    d = (self.this[i]>>(p))&km
                    if(p <= 0):
                        p += self.DB; 
                        i = i - 1
                
                if(d > 0):
                    m = True
                if(m):
                    r += self.int2char(d)
          
        if(m):
            returnstr = r
        else:
            returnstr = "0"
        return returnstr
        
    def int2char(self, n):
        return self.BI_RM[n]
       
    def intAt(self,s,i):
        #print(s)
        #print(i)
        #print(s[i])
        #print(ord(s[i]))
        c = self.BI_RC[ord(s[i])]
        #print(c)
        if(c == None):
            returnval = -1
        else:
            returnval = c
        return returnval
    
    
    
    def fromString(self,ss,b):
        k = 0
        #print(self.this)
        #print(self.BI_RC)
        
        if(b == 16):
            k = 4
        elif(b == 8): 
            k = 3
        elif(b == 256): 
            k = 8
        elif(b == 2): 
            k = 1
        elif(b == 32): 
            k = 5
        elif(b == 4): 
            k = 2
        else:
            print("fromRadix(s,b)")
            return
        self.t = 0;
        self.s = 0;
        i = len(ss)
        mi = False
        sh = 0;
        self.this = [None] * i
        
        while(i > 0):
            #print(i)
            i = i - 1
            #x = (k==8)?s[i]&0xff:intAt(s,i);
            x = 0
            if(k==8):
                if(type(ss[i]) is int):
                    x = ss[i]&0xff
                else:
                    ss[i] = int(ss[i])
                    x = ss[i]&0xff
            else:
                x = self.intAt(ss,i)
            
            if(x < 0):
                if(ss[i] == "-"):
                    mi = True;
                continue;
            
            mi = False;
            if(sh == 0):
                self.this[self.t] = x
                self.t = self.t+1
            elif(( sh + k ) > self.DB):
                
                self.this[self.t-1] |= (x & ( ( 1 << (self.DB-sh) ) -1) ) << sh
                self.this[self.t] = (x >> ( self.DB - sh ))
                self.t = self.t + 1
            
            else:
                self.this[self.t-1] |= x << sh
            sh += k
            if(sh >= self.DB):
                sh -= self.DB
            
#         print(ss[0])
        #if(k == 8 and (ss[0]&0x80) != 0):
        if(k == 8 and (int(ss[0]) &0x80) != 0):
            self.s = -1;
            if(sh > 0):
                
                self.this[self.t - 1] |= ((1<<(self.DB-sh))-1)<<sh
        
        self.clamp()
        if(mi):
            BigInteger.ZERO.subTo(self.this,self.this);
            
    def clamp(self):
        c = self.s & self.DM
        while(self.t > 0 and self.this[self.t-1] == c):
            self.t = self.t - 1;
            
    '''def Clamp(self):
      c = s & DM
      while(t > 0 and this[t-1] == c):
        --t'''
        
    def bitLength(self):
        if(self.t <= 0):
            return 0;
        return self.DB * (self.t-1) + self.nbits( self.this[self.t-1] ^ ( self.s & self.DM) )
        
    def nbits(self,x):
        r = 1
        t = rshift(x, 16)#x >>>16
        if((t) != 0):
            x = t;
            r += 16;
        t = x>>8
        if(t != 0):
            x = t; 
            r += 8; 
        t=x>>4
        if(t != 0):
            x = t; 
            r += 4;
        t = x>>2
        if((t) != 0):
            x = t; 
            r += 2; 
        t=x>>1
        if(t != 0):
            x = t; 
            r += 1; 
        return r;
            
    def modPowInt(self,e,m):
        z = None
        
        if(e < 256 or m.isEven()):
            z = Classic(m)
        else:
            z = Montgomery(m);
        return self.exp1(e,z);
    
    
    
    
    
    def exp1(self,e,z) :
        if(e > 0xffffffff or e < 1):
            return  BigInteger.ONE(self)
        r = nbi()
        #print("RRRRRRRr")
        #print(r.this)
        r2 = nbi()
        #print("RRRRRRR32222222")
        #print(r2.this)
        g = z.convert(self)
        i = self.nbits(e)-1;
        g.copyTo(r);
        #print("AFTER  RRRRRRRr")
        #print(r.this)
        
#         print("EXP1")
        #print(self.this)
#         print(i)
        while(i > 0):
            i = i -1
#             print("inside while ")
#             print(i)
            z.sqrTo(r,r2);
            if((e&(1<<i)) > 0):
                z.mulTo(r2,g,r);
            else:
                t = r; 
                r = r2; 
                r2 = t;
        
        return z.revert(r);
        

    
            
    def isEven(self):
        returnVal  = None
        if(self.t>0):
            val = (self.this[0]&1)
        else: 
            val = self.s
        
        returnVal = (val == 0)
        return returnVal
    
    def invDigit(self):
        if(self.t < 1):
            return 0;
        x = self.this[0];
        if((x&1) == 0):
            return 0;
        y = x&3
        y = (y*(2-(x&0xf)*y))&0xf
        y = (y*(2-(x&0xff)*y))&0xff
        y = (y*(2-(((x&0xffff)*y)&0xffff)))&0xffff
        y = (y*(2-x*y%self.DV))% self.DV
        returnval = None
        if( y>0):
            returnval = self.DV -y
        else:
            returnval = -y
        return returnval
    
    def compareTo(self, a):
        r = self.s - a.s;
        if(r != 0):
            return r
        i = self.t
        r = i - a.t
        if(r != 0):
            returnval = None
            if (self.s < 0):
                returnval = -r
            else:
                returnval = r
            return returnval
        
        while(i >= 0):
            i = i - 1
            r=self.this[i]-a.this[i]
            if(r != 0):
                return r;
            #i = i - 1
        return 0;
    
    def mod(self, a):
        r = nbi();
        abs().divRemTo(a,None,r);
        if(self.s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            a.subTo(r,r);
        return r;
    
    def copyTo(self, r):
        #for(i = this.t-1; i >= 0; --i):
        for i in range(self.t-1, -1,-1):
            r.this[i] = self.this[i];
        r.t = self.t;
        r.s = self.s;
        
    
    def fromInt(self, x):
        self.t = 1;
        if (x<0):
            self.s = -1
        else:
            self.s= 0
        if(x > 0):
            self.this[0] = x
        elif(x < -1):
            self.this[0] = x + self.DV
        else: 
            self.t = 0
        
    def lShiftTo(self, n,r):
        bs = n%self.DB
        cbs = self.DB-bs
        bm = (1<<cbs) -1
        ds = math.floor( n/self.DB)
        c = (self.s<<bs) & self.DM
        i = 0
        
#        for(i = this.t-1; i >= 0; --i) {
        #i = self.t-1
        #while(i >= 0):
        for i in range(self.t-1, -1, -1):
            if(self.this[i] != None):
                r.this[i+ds+1] = (self.this[i]>>cbs)|c
                c = (self.this[i]&bm)<<bs
            
        
        #for(i = ds-1; i >= 0; --i) r[i] = 0;
        i = ds-1
        for i in range(ds-1,  -1, -1):
            r.this[i] = 0;
        r.this[ds] = c;
        r.t = self.t+ds+1;
        r.s = self.s;
        r.clamp();
        #i = i - 1

    

            
    def rShiftTo(self, n,r):
        r.s = self.s;
        ds = math.floor(n/ self.DB);
        if(ds >= self.t):
            r.t = 0
            return
        bs = n%self.DB;
        cbs = self.DB-bs
        bm = (1<<bs)-1
        r.this[0] = self.this[ds]>>bs
#         for(var i = ds+1; i < this.t; ++i) {
        for i in range(ds+1, self.t, 1):
            r.this[i-ds-1] |= (self.this[i]&bm)<<cbs
            r.this[i-ds] = self.this[i]>>bs
        
        if(bs > 0):
            r.this[self.t-ds-1] |= (self.s&bm)<<cbs
        r.t = self.t-ds
        r.clamp()
        
        
    def dlShiftTo(self, n,r):
        #print(len(self.this))
#         for(i = this.t-1; i >= 0; --i) r[i+n] = this[i];
        for i in range(self.t-1, -1 , -1):
            r.this[i+n] = self.this[i]
#         for(i = n-1; i >= 0; --i) r[i] = 0;
        for i in range(n-1, -1, -1):
            r.this[i] = 0
        r.t = self.t+n;
        r.s = self.s;
    
    def drShiftTo(self, n,r):
#         for(var i = n; i < this.t; ++i) r[i-n] = this[i];
        for i in range(n, self.t, 1):
            r.this[i-n] = self.this[i]
            
        r.t = max(self.t-n,0);
        r.s = self.s;
        

        
    def subTo(self, a,r):
        i = 0
        c = 0
        m = min(a.t,self.t)
        while(i < m):
            #print(i)
            #print(self.this[i])
            #print(a.this[i])
            c = c +  self.this[i]-a.this[i]
            r.this[i] = c&self.DM;
            i = i+1
            c >>= self. DB;
        
        if(a.t < self.t):
            c -= a.s;
            while(i < self.t):
                c += self.this[i];
                r.this[i] = c&self.DM;
                c >>= self.DB;
                i = i+1
          
            c += self.s;
        
        else:
            c += self.s;
            while(i < a.t):
                c -= a.this[i]
                r.this[i] = c&self.DM
                c >>= self.DB
                i = i+1
          
            c -= a.s
        
#         r.s = (c<0)?-1:0;
        if (c<0) :
            r.s = -1
        else:
            r.s = 0
        if(c < -1):
            r.this[i] = self.DV+c
            i = i+1
        elif(c > 0):
            r.this[i] = c
            i = i+1
        r.t = i
        r.clamp()
        

    
    def divRemTo(self, m,q,r):
        pm = m.abs()
        if(pm.t <= 0):
            return
        pt = self.abs()
        if(pt.t < pm.t):
            if(q != None):
                q.fromInt(0);
            if(r != None):
                self.copyTo(r);
            return;
        
        if(r == None):
            r = nbi()
        y = nbi()
        ts = self.s
        ms = m.s
        nsh = self.DB - self.nbits(pm.this[pm.t-1])
        if(nsh > 0):
            pm.lShiftTo(nsh,y) 
            pt.lShiftTo(nsh,r)
        else:
            pm.copyTo(y)
            pt.copyTo(r); 
        ys = y.t
        y0 = y.this[ys-1]
        if(y0 == 0):
            return;
#         yt = y0*(1<<this.F1)+((ys>1)?y[ys-2]>>this.F2:0)
        if(ys>1):
            val = y.this[ys-2]>>self.F2
        else: 
            val = 0
        #print("1")
        #print(self.this)
        yt =  y0*(1<<self.F1) + val
        d1 = self.FV/yt
        d2 = (1<<self.F1)/yt
        e = 1<<self.F2;
        i = r.t
        j = i-ys
        #print("2")
        #print(self.this)
#         t = (q==null)?nbi():q;
        if (q==None):
            t = nbi()
        else:
            t = q
        y.dlShiftTo(j,t)
        #print("3")
        #print(self.this)
        if(r.compareTo(t) >= 0):
            r.this[r.t] = 1
            r.t = r.t+1
            r.subTo(t,r);
        one = BigInteger.ONE(self)
        #print("4")
        #print(self.this)
        one.dlShiftTo(ys,t);
        #print("5")
        #print(self.this)
        t.subTo(y,y);    
        while(y.t < ys):
            y.this[y.t] = 0
            y.t = y.t+1
        
        while(j >= 0):
            j = j -1
            if( j != -1):
                #if(j != -1):
        #             qd = (r[--i]==y0)?this.DM:Math.floor(r[i]*d1+(r[i-1]+e)*d2);
        
                ifcop = r.this[i]
                i = i - 1
                if  (ifcop ==y0) :
                    qd = self.DM
                else:
                    qd = math.floor(r.this[i]*d1+(r.this[i-1]+e)*d2)
                    
                r.this[i] = r.this[i] + y.am(0,qd,r,j,0,ys)
                if((r.this[i]) < qd):
                    y.dlShiftTo(j,t);
                    r.subTo(t,r);
                    #qd = qd - 1
                    while(r.this[i] < qd):
                        qd = qd - 1
                        r.subTo(t,r);
                    
            
        if(q != None):
            r.drShiftTo(ys,q);
            if(ts != ms):
                BigInteger.ZERO.subTo(q,q);
        
        r.t = ys;
        r.clamp();
        if(nsh > 0):
            r.rShiftTo(nsh,r)
        if(ts < 0):
            BigInteger.ZERO.subTo(r,r);
        

        
        
    def abs(self):
        returnVal = None
        if (self.s<0):
            returnVal = self.negate()
        else:
            returnVal = self
        return returnVal
    
    def negate(self):
        r = nbi()
        BigInteger.ZERO.subTo(self.this,r)
        return r
        
        
m = None
class Classic():
    def __init__(self, m):
        self.thism = m
    def convert(self, x):
        if(x.s < 0 or x.compareTo(self.thism) >= 0):
            return x.mod(self.thism);
        else:
            return x;
    
m = None    
class  Montgomery():
    def __init__(self, m):
        self.thism = m;
        self.thismp = m.invDigit();
        self.thismpl = self.thismp&0x7fff;
        self.thismph = self.thismp>>15;
        self.thisum = (1<<(m.DB-15))-1;
        self.thismt2 = 2*m.t;
    
    def convert(self, x):
        r = nbi()
        x.abs().dlShiftTo(self.thism.t,r)
        r.divRemTo(self.thism,None,r);
        if(x.s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            self.thism.subTo(r,r)
        return r
    
    def reduce(self, x):
        while(x.t <= self.thismt2):
            x.this[x.t] = 0
            x.t = x.t + 1
        #for(var i = 0; i < this.m.t; ++i) {
        i = 0
        for  i in range( 0, self.thism.t, 1):
            j = x.this[i]&0x7fff;
            u0 = (j*self.thismpl+(((j*self.thismph+(x.this[i]>>15)*self.thismpl)&self.thisum)<<15))&x.DM;
            j = i+self.thism.t;
            x.this[j] += self.thism.am(0,u0,x,i,0,self.thism.t);
          
            while(x.this[j] >= x.DV):
                x.this[j] = x.this[j] - x.DV; 
                j = j + 1
                x.this[j] = x.this[j] + 1
        
        x.clamp();
        x.drShiftTo(self.thism.t,x);
        if(x.compareTo(self.thism) >= 0):
            x.subTo(self.thism,x);
        

    
    def sqrTo(self, x,r):
        x.squareTo(r)
        self.reduce(r)
        
    def mulTo(self, x,y,r):
        x.multiplyTo(y,r)
        self.reduce(r)
        
    def revert(self, x):
        r = nbi()
        x.copyTo(r);
        self.reduce(r);
        return r;
        
    

class SecureRandom():
    
    def __init__(self):
        self.rng_state = None
        self.rng_pool = None
        self.rng_ppt = None
        self.rng_psize = 256
        if(self.rng_pool == None):
            self.rng_pool = [None] * 256
            self.rng_pptr = 0;
            
            while(self.rng_pptr < self.rng_psize):
                t = math.floor(65536 * random.random())
                #t = math.floor(65536 * 2)
                self.rng_pool[self.rng_pptr] = rshift(t, 8)#t >>> 8
                self.rng_pptr = self.rng_pptr + 1
                
                self.rng_pool[self.rng_pptr] = t & 255
                self.rng_pptr = self.rng_pptr + 1
            
            self.rng_pptr = 0;
            self.rng_seed_time();

            
    
    def rng_get_byte(self):
        if(self.rng_state == None):
            self.rng_seed_time();
            self.rng_state = prng_newstate()
            self.rng_state.init(self.rng_pool)
            #for(rng_pptr = 0; rng_pptr < rng_pool.length; ++rng_pptr)
            rng_pptr = 0
            for rng_pptr in range(0, len(self.rng_pool), 1):
                self.rng_pool[rng_pptr] = 0;
            self.rng_pptr = 0;
          
        return self.rng_state.next();
    
    
    def nextBytes(self, ba):
        i = 0
        lencount = 0
        for jj in range( len(ba) ):
            if(ba[jj] != None):
                lencount = lencount + 1
        for i in range( 0 , lencount, 1):# (i = 0; i < ba.length; ++i):
            ba[i] = self.rng_get_byte()
            
    
    def rng_seed_int(self, x) :
        self.rng_pool[self.rng_pptr] ^= x & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 8) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 16) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        self.rng_pool[self.rng_pptr] ^= (x >> 24) & 255
        self.rng_pptr = self.rng_pptr + 1
        
        if(self.rng_pptr >= self.rng_psize):
            self.rng_pptr = self.rng_pptr - self.rng_psize
        
    
    def rng_seed_time(self):
        self.rng_seed_int(round(time.time() * 1000))
        #self.rng_seed_int(1498555878795)
    
   
def encryptForm():
    rsa = RSAKey();
    rsa.setPublic( "BB955F6C6185B341C1A42EBF1FF9971B273878DBDAB252A0F1C305EBB529E116D807E0108BE6EDD47FF8DC5B6720FFE7F413CBB4ACDFB4C6BE609A5D60F5ADB261690A77755E058D4D9C0EC4FC2F5EB623DEBC88896003FBD8AFC4C3990828C66062A6D6CE509A2B0F8E06C4E332673FB86D235164B62B6110C1F1E0625B20ED", "10001");
    res = rsa.encrypt("credit123");
    print(res)   
    
encryptForm()

#%%