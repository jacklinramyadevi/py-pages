
import time
import math
from _operator import rshift
import random
import traceback
import ctypes

class mailEncrypt():
    
    def funca(self, a, d):
        c = (a & 65535) + (d & 65535);
        return self.bitwiseLessthan( ((self.bitwiseGreaterthan(a , 16)) + (self.bitwiseGreaterthan(d , 16)) + (self.bitwiseGreaterthan(c , 16)) ), 16) | c & 65535
    
    def bitwiseLessthan(self, val, point):
        try:
            return ctypes.c_int(val << point ^ 0).value
        except:
            print(traceback.format_exc())   
            return 0
        
    def bitwiseGreaterthan(self, val, point):
        try:
            return ctypes.c_int(val >> point ^ 0).value
        except:
            print(traceback.format_exc())   
            return 0
        
    def rshift1(self, val, n): 
        return (val % 0x100000000) >> n
    
    def calcDigest(self, b):
        try:
            #for (var d = (b.length + 8 >> 6) + 1, c = Array(16 * d), e = 0; e < 16 * d; e++)
            c = [0] * 16
            e = 0
            d = 1
            
            #for (e = 0; e < b.length; e++)
            for e in range (0, len(b), 1):
                #c[e >> 2] |= b.charCodeAt(e) << 24 - 8 * (e & 3);
                c[e >> 2] |= ord(b[e]) << 24 - 8 * (e & 3);
            e = e + 1
            c[e >> 2] |= 128 << 24 - 8 * (e & 3);
            c[16 * d - 1] = 8 * len(b)
            b = [None] * 80
    #         for (var d = 1732584193, e = -271733879, f = -1732584194, h = 271733878, j = -1009589776, k = 0; k < c.length; k += 16) {
            e = -271733879
            f = -1732584194
            h = 271733878
            j = -1009589776
            k = 0
            d = 1732584193
            for  k in range ( 0, len(c), 16) :
                
                #for (var m = d, n = e, p = f, q = h, r = j, g = 0; 80 > g; g++) {
                m = d
                n = e
                p = f
                q = h
                r = j
                g = 0
                for g in range( 0,  80, 1):
                    
                    b[g] = c[k + g] if 16 > g else self.bitwiseLessthan((b[g - 3] ^ b[g - 8] ^ b[g - 14] ^ b[g - 16]) , 1) | self.rshift1((b[g - 3] ^ b[g - 8] ^ b[g - 14] ^ b[g - 16]), 31)
                    
                    #l = d << 5 | d >>> 27, s
                    #l =  d << 5 | rshift(d ,27)
                    l = self.bitwiseLessthan(d, 5)  | self.rshift1(d ,27)
                    #s = 20 > g ? e & f | ~e & h : 40 > g ? e ^ f ^ h : 60 > g ? e & f | e & h | f & h : e ^ f ^ h;
                    if (20 > g):
                        cond1 = e & f | ~e & h
                    else:
                        if(40 > g):
                            cond1 = e ^ f ^ h
                        else:
                            if(60 > g): 
                                cond1 = e & f | e & h | f & h
                            else:
                                cond1 = e ^ f ^ h
                    
                    s = cond1       
                    #l = a(a(l, s), a(a(j, b[g]), 20 > g ? 1518500249 : 40 > g ? 1859775393 : 60 > g ? -1894007588 : -899497514));
                    #l = a(a(l, s), a(a(j, b[g]), 20 > g ? 1518500249 : 40 > g ? 1859775393 : 60 > g ? -1894007588 : -899497514));
                    
                    l = self.funca(self.funca(l, s), self.funca(self.funca(j, b[g]), 1518500249 if 20 > g else 1859775393 if 40 > g else -1894007588 if 60 > g else -899497514))

                    
                           
                    j = h;
                    h = f;
                    #rishi = e >>> 2
#                     rishi = rshift(e, 2)
                    #f = e << 30 | rishi
                    f = self.bitwiseLessthan(e, 30) | self.rshift1(e, 2)
                    e = d
                    d = l
                
                d = self.funca(d, m)
                e = self.funca(e, n)
                f = self.funca(f, p)
                h = self.funca(h, q)
                j = self.funca(j, r)
            
            c = [d, e, f, h, j]
            b = ""
            #for (d = 0; d < 4 * c.length; d++)
            for d in range( 0,  4 * len(c), 1):
                #b += "0123456789abcdef".charAt(c[d >> 2] >> 8 * (3 - d % 4) + 4 & 15) + "0123456789abcdef".charAt(c[d >> 2] >> 8 * (3 - d % 4) & 15)
                b += "0123456789abcdef"[c[d >> 2] >> 8 * (3 - d % 4) + 4 & 15] + "0123456789abcdef"[(c[d >> 2] >> 8 * (3 - d % 4) & 15)]
                
            return b
        except Exception:
            print(traceback.format_exc())
    

def encryptForm():
    rsa = mailEncrypt()
    res = rsa.calcDigest("fetion.com.cn:Dakshan04")
    print(res)   
    
encryptForm()