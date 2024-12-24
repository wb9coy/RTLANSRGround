import packetDefs
import ctypes

class processGPSData():
    def __init__(self,
                 debug=False):
        self.GGA          = ""
        self.RMC          = ""
        self.debug        = debug
        
        
    def chksum(self, inp): # GPS message checksum verification
        if not inp.startswith("$"): return False
        if not inp[-3:].startswith("*"): return False
        payload = inp[1:-3]
        checksum = 0
        for i in range(len(payload)):
            checksum =  checksum ^ ord(payload[i])
        if(self.debug):
            print("%02X" % checksum)
            print(inp[-2:])
        return ("%02X" % checksum) == inp[-2:]        
   
    def GGAPacket(self,packet):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        ctypes.memmove(ctypes.pointer(HABPacketGPSData), packet, ctypes.sizeof(HABPacketGPSData))
        self.GGA = ""
        for indx in range(HABPacketGPSData.gpsDataLen):
            self.GGA = self.GGA + chr(HABPacketGPSData.gpsData[indx])
            
        if self.debug:
            print(self.GGA)
            
        self.GGA = self.GGA.replace("\r\n", "") 
        return self.GGA
        
    def GGA1Packet(self,packet):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        ctypes.memmove(ctypes.pointer(HABPacketGPSData), packet, ctypes.sizeof(HABPacketGPSData))
        self.GGA = ""
        for indx in range(HABPacketGPSData.gpsDataLen):
            self.GGA = self.GGA + chr(HABPacketGPSData.gpsData[indx])
        
    def GGA2Packet(self,packet):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        ctypes.memmove(ctypes.pointer(HABPacketGPSData), packet, ctypes.sizeof(HABPacketGPSData))
        for indx in range(HABPacketGPSData.gpsDataLen):
            self.GGA = self.GGA + chr(HABPacketGPSData.gpsData[indx])
            
        if self.debug:
            print(self.GGA)
            
        self.GGA = self.GGA.replace("\r\n", "") 
        return self.GGA
        
    def RMCPacket(self,packet):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        ctypes.memmove(ctypes.pointer(HABPacketGPSData), packet, ctypes.sizeof(HABPacketGPSData))
        self.RMC = ""
        for indx in range(HABPacketGPSData.gpsDataLen):
            self.RMC = self.RMC + chr(HABPacketGPSData.gpsData[indx])
            
        if self.debug:
            print(self.RMC)
            
        self.RMC = self.RMC.replace("\r\n", "")   
        return self.RMC
        
    def RMC1Packet(self,packet):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        ctypes.memmove(ctypes.pointer(HABPacketGPSData), packet, ctypes.sizeof(HABPacketGPSData))
        self.RMC = ""
        for indx in range(HABPacketGPSData.gpsDataLen):
            self.RMC = self.RMC + chr(HABPacketGPSData.gpsData[indx])
        
    def RMC2Packet(self,packet):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        ctypes.memmove(ctypes.pointer(HABPacketGPSData), packet, ctypes.sizeof(HABPacketGPSData))
        for indx in range(HABPacketGPSData.gpsDataLen):
            self.RMC = self.RMC + chr(HABPacketGPSData.gpsData[indx])
            
        if self.debug:
            print(self.RMC)
            
        self.RMC = self.RMC.replace("\r\n", "")          
        return self.RMC