import packetDefs
import ctypes
import  libscrc

class processPressureData():
    def __init__(self,
                 debug=False):
        self.debug        = debug
        
    def pressureDataPacket(self,packet):
        
        rtn = True
        pressureInfoData = None
        
        HABPacketPressureInfoData = packetDefs.HABPacketPressureInfoDataType()
        ctypes.memmove(ctypes.pointer(HABPacketPressureInfoData), packet, ctypes.sizeof(HABPacketPressureInfoData))
        
        tempLen =  ctypes.sizeof(HABPacketPressureInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketPressureInfoData )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketPressureInfoData .crc16 == crc16):
            rtn = True               
            pressureInfoData = "{:.1f}hPa".format(HABPacketPressureInfoData.pressureInfoData)
            if(self.debug):
                print(pressureInfoData)
            
        return rtn,pressureInfoData