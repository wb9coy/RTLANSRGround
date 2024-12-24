import os
import threading
import time
import ctypes
import reedsolo
import packetDefs
import processImageData
import processInfoData
import processGPSData
import processCallSignData
import processBattData
import processIntTempData
import processExtTempData
import processHumidityData
import processPressureData

class processPayload():
    def __init__(self,
                 payloadQueue,
                 webClientQueue,
                 udpLocationQueue, 
                 ftpClientQueue,
                 imageFileDir,
                 imageSeqFileDir,
                 dataLoggerObj,
                 gwID,
                 is_windows,
                 debug=False):

        self.payloadQueue          = payloadQueue 
        self.webClientQueue        = webClientQueue
        self.udpLocationQueue = udpLocationQueue
        self.ftpClientQueue        = ftpClientQueue
        self.imageFileDir          = imageFileDir
        self.imageSeqFileDir       = imageSeqFileDir
        self.dataLoggerObj         = dataLoggerObj
        self.gwID                  = gwID
        self.is_windows            = is_windows
        self.debug                 = debug
        self.runable               = True
        self.processPayloadThread  = None
        self.rsc = reedsolo.RSCodec(packetDefs.NPAR, fcr=1)
        self.timeout               = 5

    async def STOP(self):
        self.runable = False
        self.payloadQueue.put(b'0x0')
        
    async def rsDecode(self, encodedData):
        rtn = True
        decodedData = None
        try:
            data, rmesecc, errata_pos = self.rsc.decode(encodedData) 
            decodedData = bytes(data)
        except Exception as e:
            print(e)
            rtn = False
            
        return rtn, decodedData
       
        
    async def processPayloadLoopFunc(self):
        print("**** Starting Payload Processing ******")
        
        processImageDataObj    = processImageData.processImageData(self.imageFileDir,self.imageSeqFileDir,self.gwID,self.ftpClientQueue,is_windows=self.is_windows)
        processInfoDataObj     = processInfoData.processInfoData()
        processGPSDataObj      = processGPSData.processGPSData()
        processCallSignDataObj = processCallSignData.processCallSignData()
        processBattDataObj     = processBattData.processBattData()
        processIntTempDataObj  = processIntTempData.processIntTempData()
        processExtTempDataObj  = processExtTempData.processExtTempData()
        processHumidityDataObj = processHumidityData.processHumidityData()
        processPressureDataObj = processPressureData.processPressureData()
        
        snrCount = 0
        snrAvg = 0
        
        if os.path.exists(self.imageFileDir) == False:
            os.mkdir(self.imageFileDir)

        while self.runable:
            try:
                qData = await self.payloadQueue.get()
                rtn = True
                #try:
                    #packetId = int.from_bytes(qData[0][0:1], "little")
                    #packetLen = self.packetLen(packetId)
                    #data, rmesecc, errata_pos = rsc.decode(qData[0][:packetLen]) 
                    #data = bytes(data)
                #except Exception as e:
                    #print(e)
                    #rtn = False                
                snr = qData[1]
                packetId = int.from_bytes(qData[0][0:1], "little")
                
                if( packetId == packetDefs.START_IMAGE):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketImageStartType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                    
                        await processImageDataObj.imageStart(data)
                    else:
                        print("rsDecode Fail START_IMAGE")                        
                    
                if( packetId == packetDefs.IMAGE_DATA):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketImageDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    #temp =  qData[0][:packetLen]
                    #for b in temp:
                        #print(b)
                    if(rtn):
                        processImageDataObj.imageBody(data)
                    else:
                        print("rsDecode Fail IMAGE_DATA")                       
                
                if( packetId == packetDefs.END_IMAGE):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketImageEndType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                    
                        await processImageDataObj.imageEnd(data)
                    else:
                        print("rsDecode Fail END_IMAGE")    
                    
                if( packetId == packetDefs.INFO_DATA):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketInfoDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                       
                        infoData = processInfoDataObj.infoDataPacket(data)
                        self.dataLoggerObj.LOG(infoData)
                    else:
                        print("rsDecode Fail INFO_DATA")  
    
                if( packetId == packetDefs.GPS_GGA_1):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketGPSDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                     
                        processGPSDataObj.GGA1Packet(data)
                    else:
                        print("rsDecode Fail GPS_GGA_1")  
                    
                if( packetId == packetDefs.GPS_GGA_2):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketGPSDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                     
                        GGA = processGPSDataObj.GGA2Packet(data)
                        if(processGPSDataObj.chksum(GGA)):
                            self.webClientQueue.put(GGA)
                            self.dataLoggerObj.LOG(GGA)
                            self.udpLocationQueue.put(GGA)
                        else:
                            print("Failed GGA Checksum")
                    else:
                        print("rsDecode Fail GPS_GGA_2")  
                    
                if( packetId == packetDefs.GPS_GGA):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketGPSDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):
                        GGA = processGPSDataObj.GGAPacket(data)
                        if(processGPSDataObj.chksum(GGA)):
                            GGA = processGPSDataObj.GGAPacket(data)
                            self.webClientQueue.put(GGA)
                            self.dataLoggerObj.LOG(GGA)
                            self.udpLocationQueue.put(GGA)
                        else:
                            print("Failed GGA Checksum")                            
                    else:
                        print("rsDecode Fail GPS_GGA")  
                    
                if( packetId == packetDefs.GPS_RMC_1):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketGPSDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                      
                        processGPSDataObj.RMC1Packet(data)
                    else:
                        print("rsDecode Fail GPS_RMC_1")  
                    
                if( packetId == packetDefs.GPS_RMC_2):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketGPSDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                       
                        RMC = processGPSDataObj.RMC2Packet(data)
                        if(processGPSDataObj.chksum(RMC)):
                            self.webClientQueue.put(RMC)
                            self.dataLoggerObj.LOG(RMC)
                        else:
                            print("Failed RMC Checksum")                             
                    else:
                        print("rsDecode Fail GPS_RMC_2")  
                    
                if( packetId == packetDefs.GPS_RMC):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketGPSDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                       
                        RMC = processGPSDataObj.RMCPacket(data)
                        if(processGPSDataObj.chksum(RMC)):
                            self.webClientQueue.put(RMC)
                            self.dataLoggerObj.LOG(RMC)
                        else:
                            print("Failed RMC Checksum")                               
                    else:
                        print("rsDecode Fail GPS_RMC")                      
                    
                if( packetId == packetDefs.CW_ID):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketCallSignDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                      
                        rtn,callSign = processCallSignDataObj.callSignDataPacket(data)
                        if(rtn):
                            webMsg = "$CALL " + callSign
                            self.webClientQueue.put(bytes(webMsg,'utf-8'))
                            self.dataLoggerObj.LOG(webMsg)
                        else:
                            print("rsDecode Fail CW_ID") 
                    
                if( packetId == packetDefs.BATT_INFO):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketBattInfoDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                      
                        rtn, battVoltage = processBattDataObj.battDataPacket(data)
                        if(rtn):
                            webMsg = "$BATT " + battVoltage
                            self.webClientQueue.put(bytes(webMsg,'utf-8'))
                            self.dataLoggerObj.LOG(webMsg)
                        else:
                            print("rsDecode Fail BATT_INFO")                             
                    
                if( packetId == packetDefs.INT_TEMP):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketIntTempInfoDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                      
                        rtn,intTempVal = processIntTempDataObj.intTempPacket(data)
                        if(rtn):
                            webMsg = "$INT_TEMP " + intTempVal
                            self.webClientQueue.put(bytes(webMsg,'utf-8'))
                            self.dataLoggerObj.LOG(webMsg)
                    else:
                        print("rsDecode Fail INT_TEMP")                         
                        
                if( packetId == packetDefs.EXT_TEMP):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketExtTempInfoDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                       
                        rtn,extTempVal = processExtTempDataObj.extTempPacket(data)
                        if(rtn):
                            webMsg = "$EXT_TEMP " + extTempVal
                            self.webClientQueue.put(bytes(webMsg,'utf-8'))
                            self.dataLoggerObj.LOG(webMsg)
                    else:
                        print("rsDecode Fail EXT_TEMP") 
                    
                if( packetId == packetDefs.HUM_INFO):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketHumidityInfoDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                       
                        rtn,humVal = processHumidityDataObj.humidityDataPacket(data)
                        if(rtn):
                            webMsg = "$HUM " + humVal
                            self.webClientQueue.put(bytes(webMsg,'utf-8'))
                            self.dataLoggerObj.LOG(webMsg)
                    else:
                        print("rsDecode Fail HUM_INFO") 
                            
                if( packetId == packetDefs.PRESS_INFO):
                    packetLen = ctypes.sizeof(packetDefs.HABPacketPressureInfoDataType)
                    rtn, data = await self.rsDecode(qData[0][:packetLen])
                    if(rtn):                     
                        rtn,pressVal = processPressureDataObj.pressureDataPacket(data)
                        if(rtn):
                            webMsg = "$PRES " + pressVal
                            self.webClientQueue.put(bytes(webMsg,'utf-8'))
                            self.dataLoggerObj.LOG(webMsg)
                    else:
                        print("rsDecode Fail PRESS_INFO") 
                
                snrCount += 1
                snrAvg += snr
                if(snrCount % 50 == 0):
                    intVal = int(snrAvg/50)
                    print("***********SNR" + str(intVal))
                    webMsg = "$RSSI_GW" + str(self.gwID) + " " + str(intVal)
                    self.webClientQueue.put(bytes(webMsg,'utf-8'))
                    self.dataLoggerObj.LOG(webMsg)                    
                    snrAvg = 0
                    
                        
            except:
                pass
                     
        print("**** Ending Process Payload Loop ******")