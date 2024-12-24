import packetDefs
import ctypes
import libscrc

class processIntTempData():
    def __init__(self,
                 debug=False):
        self.debug        = debug
        
    def intTempPacket(self,packet):
        rtn = False
        
        HABPacketIntTempInfoData = packetDefs.HABPacketIntTempInfoDataType()
        ctypes.memmove(ctypes.pointer(HABPacketIntTempInfoData), packet, ctypes.sizeof(HABPacketIntTempInfoData))
        tempLen =  ctypes.sizeof(HABPacketIntTempInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketIntTempInfoData )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketIntTempInfoData .crc16 == crc16):
            rtn = True
            intTempInfoData = "{:.1f}F".format(HABPacketIntTempInfoData.intTempInfoData)
            if(self.debug):
                print(intTempInfoData)
                
        return rtn,intTempInfoData