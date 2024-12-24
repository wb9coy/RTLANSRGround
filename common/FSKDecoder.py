import os
import sys
import time
import queue
import threading
import ctypes
import asyncio
import numpy as np
from bitstring import BitArray

import searcher
sys.path.append('common')
import FSKTypes

def _bitToBytes(bitList):
    tempList = []
    for j in range(0,len(bitList),8):
        tempBitList = bitList[j:j+8]
        bitsAsInt = BitArray(tempBitList)
        tempList.append(bitsAsInt.uint)
    payloadBytes = bytes(tempList)
    return payloadBytes    

class FSKDecoder():
    def __init__(self,
                 decoderQueue,
                 payloadQueue,
                 debug=False):

        self.decoderQueue   = decoderQueue
        self.payloadQueue   = payloadQueue
        self.runable        = True
        self.decoderThread  = None
        self.debug          = debug
        self.timeout        = 5 

    async def STOP(self):
        self.runable = False
        await self.decoderQueue.put(b'0x0')
            
    async def decoderLoopFunc(self):
        print("**** Starting Decoder ******")
        
        debugCounter        = 0
        MTU                 = 64
        
        preambleSearchState = 0
        syncSearchState     = 1
        processPayloadState = 2
        STATE               = preambleSearchState
        
        # Preamble pattern
        ba           = BitArray(hex="0x55"*4).bin
        preamble     = []
        for i in ba:
                preamble.append(int(i))     
        preambleSearcherhObj = searcher.searcher(preamble)
        
        # Sync pattern
        ba       = BitArray(hex="0x080 x6d 0x53 0x88").bin
        sync     = []
        for i in ba:
            sync.append(int(i)) 
        syncSearcherhObj    = searcher.searcher(sync)
        syncRetryCountLimit = len(sync) + len(preamble)
        syncCount           = 0
        
        #decoded bits
        bitList     = []
        
        payloadRetryCountLimit = (MTU *8)
        payloadCount           = 0              

        debugCounter = 0
        nin          = 320
        snr = None
        try:
            while self.runable:
                bitbuf = await self.decoderQueue.get()
                if(self.runable):
                    #print("self.decoderQueue.get()" + str(self.decoderQueue.qsize()))
                    #self.debug = True
                    #if(self.debug):                    
                        #for bit in bitbuf[0]:
                            #if debugCounter % nin == 0:
                                #print("")
                            #debugCounter +=1
                            #print(bit,end='')
                        #print("")
                    snr =  bitbuf[1]
                    for bit in bitbuf[0]:                
                        preambleSearcherhObj.add(bit)
                        preambleSearchResult = preambleSearcherhObj.detected()
                        if(preambleSearchResult == True):
                            #print("preamble Detected")
                            STATE     = syncSearchState
                            syncCount = 0
                            syncSearcherhObj.reset()                 
                            
                        if(STATE == processPayloadState):
                            #print("processPayloadState")
                            bitList.append(bit)
                            payloadCount += 1
                            #print(payloadCount)
                            if(payloadCount == payloadRetryCountLimit):
                                if(self.debug):
                                    #bitList[20] = 0
                                    #bitList[21] = 0
                                    #bitList[22] = 0
                                    #bitList[23] = 0                                
                                    #bitList[25] = 0
                                    #bitList[26] = 0                                
                                    #bitList[30] = 0
                                    bitList[31] = 0
                                    bitList[32] = 0
                                    bitList[33] = 0                                
                                    bitList[35] = 0
                                    bitList[36] = 0
                                    bitList[40] = 0
                                    bitList[41] = 0
                                    bitList[45] = 0
                                    bitList[46] = 0
                                    bitList[50] = 0
                                    bitList[51] = 0
                                    bitList[55] = 0
                                    bitList[66] = 0
                                    bitList[70] = 0
                                    bitList[71] = 0
                                    bitList[75] = 0
                                    bitList[76] = 0
                                    bitList[80] = 0
                                    bitList[81] = 0
                                    bitList[82] = 0
                                    bitList[83] = 0
                                    bitList[85] = 0
                                    bitList[86] = 0
                                    bitList[87] = 0
                                    bitList[88] = 0                                  
                                    bitList[91] = 0
                                    bitList[95] = 0
                                    bitList[96] = 0                                  
                                payloadBytes = _bitToBytes(bitList)
                                #print(payloadBytes)
                                #print("Get Bytes")
                                #print(payloadBytes)
                                await self.payloadQueue.put([payloadBytes, snr])
                                STATE     = preambleSearchState
                                bitList = []
                                #print("Payload Done")                
                            
                        if(STATE == syncSearchState):
                            #print("syncSearchState")
                            syncSearcherhObj.add(bit)
                            syncSearchResult = syncSearcherhObj.detected()
                            if(syncSearchResult == True):
                                #print("Sync Done")
                                STATE = processPayloadState
                                bitList = []
                                payloadCount = 0
                            else:
                                syncCount += 1
                                if(syncCount == syncRetryCountLimit):
                                    STATE     = preambleSearchState                   
        except asyncio.CancelledError:
            pass
            
        print("decoderLoopFunc Done")