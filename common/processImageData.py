import os
import queue
import asyncio
import packetDefs
import utils
import ctypes
import ftpClientProc
import libscrc

class processImageData():
    def __init__(self,
                 imageFileDir,
                 imageSeqFileDir,
                 gwID,
                 ftpClientQueue,
                 is_windows,
                 debug=False):
        self.imageFileDir    = imageFileDir
        self.imageSeqFileDir = imageSeqFileDir
        self.gwID            = gwID
        self.ftpClientQueue  = ftpClientQueue
        self.is_windows      = is_windows        

        self.prevSeqNum      = -1
        self.fileHandle      = None
        self.seqFileHandle   = None        
        self.debug           = debug
        
    async def imageStart(self,packet):
        HABPacketImageStart = packetDefs.HABPacketImageStartType()
        ctypes.memmove(ctypes.pointer(HABPacketImageStart), packet, ctypes.sizeof(HABPacketImageStart))
        tempLen =  ctypes.sizeof(HABPacketImageStart ) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketImageStart )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketImageStart .crc16 == crc16):
            JpegPathName = utils.getJpegPathName(self.imageFileDir,HABPacketImageStart.imageFileID,self.is_windows)
            print("Start Image " + JpegPathName)
            if(self.fileHandle != None):
                self.fileHandle.close()
                await asyncio.sleep(.1)
            self.prevSeqNum   = -1
            self.fileHandle = open(JpegPathName, "wb")
            await asyncio.sleep(.1)
            
            HABPacketImageSeqStart = packetDefs.HABPacketImageSeqStartType()
            imageSeqFilePathName = utils.getImageSeqFilePathName(self.imageSeqFileDir,HABPacketImageStart.imageFileID,self.gwID ,self.is_windows)
    
            if(self.seqFileHandle != None):
                self.seqFileHandle.close()
                await asyncio.sleep(.1)
            self.seqFileHandle = open(imageSeqFilePathName, "wb")
            await asyncio.sleep(.1)
            if(self.seqFileHandle):
                HABPacketImageSeqStart.packetType  = packetDefs.START_SEQ_IMAGE
                HABPacketImageSeqStart.imageFileID = HABPacketImageStart.imageFileID
                HABPacketImageSeqStart.gwID        = self.gwID
                HABPacketImageSeqStart.fileSize    = HABPacketImageStart.fileSize
                self.seqFileHandle.write(HABPacketImageSeqStart)
        else:
            print("Start Image CRC Fail")
                     
    def imageBody(self,packet):
        HABPacketImageData = packetDefs.HABPacketImageDataType()
        ctypes.memmove(ctypes.pointer(HABPacketImageData), packet, ctypes.sizeof(HABPacketImageData))
        
        print(HABPacketImageData.imageSeqnum)
        if (self.prevSeqNum +1) != HABPacketImageData.imageSeqnum:
            print("********** SEQ ERROR *********" + str(HABPacketImageData.imageSeqnum))
        self.prevSeqNum = HABPacketImageData.imageSeqnum
            
        if(self.fileHandle != None):
            self.fileHandle.write(HABPacketImageData.imageData)
        
            HABPacketImageSeqData              = packetDefs.HABPacketImageSeqDataType()
            HABPacketImageSeqData.packetType   = packetDefs.IMAGE_SEQ_DATA
            HABPacketImageSeqData.imageFileID  = HABPacketImageData.imageFileID
            HABPacketImageSeqData.imageSeqnum  = HABPacketImageData.imageSeqnum
            HABPacketImageSeqData.imageDataLen = HABPacketImageData.imageDataLen
            HABPacketImageSeqData.gwID         = self.gwID
            HABPacketImageSeqData.imageData[:] = HABPacketImageData.imageData
            self.seqFileHandle.write(HABPacketImageSeqData)
    
    async def imageEnd(self,packet):
        HABPacketImageEnd = packetDefs.HABPacketImageEndType()
        ctypes.memmove(ctypes.pointer(HABPacketImageEnd), packet, ctypes.sizeof(HABPacketImageEnd))
        
        tempLen =  ctypes.sizeof(HABPacketImageEnd ) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketImageEnd )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketImageEnd .crc16 == crc16):              
            if(self.fileHandle != None):
                self.fileHandle.close()
                await asyncio.sleep(.1)
            print("End Image")
            self.fileHandle = None
         
            if(self.seqFileHandle != None):   
                HABPacketImageSeqEnd              = packetDefs.HABPacketImageSeqEndType()
                HABPacketImageSeqEnd.packetType   = packetDefs.END_SEQ_IMAGE
                HABPacketImageSeqEnd.imageFileID  = HABPacketImageEnd.imageFileID
                HABPacketImageSeqEnd.gwID         = self.gwID 
                self.seqFileHandle.write(HABPacketImageSeqEnd)
                self.seqFileHandle.close()
                await asyncio.sleep(.1)
                self.seqFileHandle = None
                try:
                    self.ftpClientQueue.put_nowait((HABPacketImageSeqEnd.imageFileID,self.gwID))
                    if(self.debug):
                        print("FTP Put queue " + str(HABPacketImageSeqEnd.imageFileID))
                except Exception as err:
                    print(f"Exception {err=}, {type(err)=}")