import packetDefs
import ctypes
import libscrc

class processInfoData():
    def __init__(self,
                 debug=False):
        self.debug        = debug
        
    def infoDataPacket(self,packet):
        HABPacketInfoData = packetDefs.HABPacketInfoDataType()
        ctypes.memmove(ctypes.pointer(HABPacketInfoData), packet, ctypes.sizeof(HABPacketInfoData))
        tempLen =  ctypes.sizeof(HABPacketInfoData ) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketInfoData )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        s = ""
        if(HABPacketInfoData .crc16 == crc16):
            for indx in range(HABPacketInfoData.infoDataLen):
                s = s + chr(HABPacketInfoData.infoData[indx])
            print(s)
        return s
        
