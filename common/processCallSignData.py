import packetDefs
import ctypes
import libscrc

class processCallSignData():
    def __init__(self,
                 debug=False):
        self.debug        = debug
        
    def callSignDataPacket(self,packet):
        rtn      = False
        callSign = None
        
        HABPacketCallSignData = packetDefs.HABPacketCallSignDataType()
        ctypes.memmove(ctypes.pointer(HABPacketCallSignData), packet, ctypes.sizeof(HABPacketCallSignData))
        tempLen =  ctypes.sizeof(HABPacketCallSignData) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketCallSignData )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketCallSignData .crc16 == crc16):
            rtn      = True
            callSign = ""
            for indx in range(HABPacketCallSignData.callSignDataLen):
                callSign = callSign + chr(HABPacketCallSignData.callSignData[indx])
            if(self.debug):
                print(s)
                
        return rtn,callSign