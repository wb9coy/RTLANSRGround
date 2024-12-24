import packetDefs
import ctypes
import libscrc

class processExtTempData():
    def __init__(self,
                 debug=False):
        self.debug        = debug
        
    def extTempPacket(self,packet):
        rtn = False
        
        HABPacketExtTempInfoData = packetDefs.HABPacketExtTempInfoDataType()
        ctypes.memmove(ctypes.pointer(HABPacketExtTempInfoData), packet, ctypes.sizeof(HABPacketExtTempInfoData))
        tempLen =  ctypes.sizeof(HABPacketExtTempInfoData ) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketExtTempInfoData )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketExtTempInfoData .crc16 == crc16):
            rtn = True
            extTempInfoData = "{:.1f}F".format(HABPacketExtTempInfoData.extTempInfoData)
            if(self.debug):
                print(extTempInfoData)
            
        return rtn,extTempInfoData