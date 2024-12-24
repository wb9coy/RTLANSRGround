import packetDefs
import ctypes
import libscrc

class processBattData():
    def __init__(self,
                 debug=False):
        self.debug        = debug
        
    def battDataPacket(self,packet):
        rtn = False
        battInfoData = None
        
        HABPacketBattInfoData = packetDefs.HABPacketBattInfoDataType()
  
        ctypes.memmove(ctypes.pointer(HABPacketBattInfoData), packet, ctypes.sizeof(HABPacketBattInfoData))
        tempLen =  ctypes.sizeof(HABPacketBattInfoData ) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketBattInfoData)
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketBattInfoData.crc16 == crc16):
            rtn = True
            battInfoData = "{:.1f}V".format(HABPacketBattInfoData.battInfoData)
            if(self.debug):
                print(battInfoData)
        
        return rtn,battInfoData