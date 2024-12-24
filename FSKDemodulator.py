import os
import sys
import ctypes
import asyncio
import rtlsdr
from bitstring import BitArray
from scipy import signal

sys.path.append('common')
import FSKTypes

class FSKDemodulator():
    def __init__(self,
                 sdr,
                 sampleQueue,
                 decoderQueue,
                 scaler,
                 debug=False):
        self.sdr              = sdr
        self.sampleQueue      = sampleQueue
        self.decoderQueue     = decoderQueue
        self.modbufQueue      = asyncio.Queue()
        self.scaler           = scaler
        self.sizeOfbitbuf     = 0
        self.sizeOfmodbuf     = 0 
        self.bitbuf           = None
        self.modbuf           = None
        self.runable          = True
        self.debugCounter     = 0
        self.libfsk           = None
        self.streamer         = None
        self.debug            = debug 
    
    async def STOP(self):
        self.runable = False
        await self.sampleQueue.put(b'0x0')
    
    def initialize(self,Fs,Rs,M,P,Nsym,is_windows):

        if(is_windows):
            self.libfsk = ctypes.WinDLL(os.getcwd() + "\\lib\\libfsk.dll")
        else:
            self.libfsk = ctypes.CDLL(os.getcwd() + "/lib/libfsk.so")        
        
        sizeOfbitbuf    = ctypes.c_int(0);
        sizeOfmodbuf    = ctypes.c_int(0);  
        psizeOfbitbuf   = ctypes.pointer(sizeOfbitbuf)
        psizeOfmodbuf   = ctypes.pointer(sizeOfmodbuf)        
        
        FSK_NONE        = -1
        self.libfsk.initialize(Fs,Rs,M,P,Nsym,FSK_NONE,FSK_NONE,psizeOfbitbuf,psizeOfmodbuf)
        self.bitbuf = (ctypes.c_uint8 * sizeOfbitbuf.value)()
        self.modbuf = (FSKTypes.COMP  * sizeOfmodbuf.value)()
        
        #sample_rate          = Fs * self.scaler
        #self.bytesPerSample  = int(sample_rate/ 8)
    
    async def sampleLoopFunc(self):
        print("**** Starting SDR Sampling ******")
        
        if(self.runable):
            async for samples in self.sdr.stream(num_samples_or_bytes=1024*128):
                #await asyncio.sleep(self.sampleQueue.qsize()*.001)
                bb = None
                if(self.runable):
                    bb = signal.decimate(samples, self.scaler)
                    await self.sampleQueue.put(bb)
                    #print("self.sampleQueue.put()" + str(self.sampleQueue.qsize()))
                else:
                    print("***********break")
                    break
        
        print("sampleLoopFunc Done")
        
    async def demodulatorLoopFunc(self):
        print("**** Starting Demodulator ******")  
        sampleData     = None
        sampleData     = await self.sampleQueue.get()
        #print("self.sampleQueue.get()" + str(self.sampleQueue.qsize()))
        sampleDataIndx = 0        
        
        sampleDataIndx = 0
        try:
            while(self.runable):
                nin = self.libfsk.getNin()
                for modIndx in range(nin):
                    if(sampleDataIndx == len(sampleData)):
                        sampleData     = None
                        sampleData     = await self.sampleQueue.get()
                        #print("self.sampleQueue.get()" + str(self.sampleQueue.qsize()))
                        sampleDataIndx = 0
                    if(self.runable):
                        modebufElement = FSKTypes.COMP()         
                        modebufElement.real = sampleData[sampleDataIndx].real
                        modebufElement.imag = sampleData[sampleDataIndx].imag
                        #print(modebufElement.real)
                        #print(modebufElement.imag)
                        self.modbuf[modIndx] = modebufElement
                        sampleDataIndx +=1
                        
                if(self.runable):
                    rtn = self.libfsk.demod(self.bitbuf, self.modbuf)
                    if(rtn == 1):
                        snr =  self.libfsk.getSNR()
                        await self.decoderQueue.put([self.bitbuf, snr])
                        await asyncio.sleep(0.0)
                        ##print("self.decoderQueue.put()" + str(self.decoderQueue.qsize()))
                        #await asyncio.sleep(0.0)
                        #self.debug = False
                        #if(self.debug):                    
                            #for bit in self.bitbuf:
                                #if self.debugCounter % nin == 0:
                                    #print("")
                                #self.debugCounter +=1
                                #print(bit,end='')
                            #print("demodulatorLoopFunc")
                            #print("")
        except asyncio.CancelledError:
            pass                            
           
        print("demodulatorLoopFunc Done")      
        