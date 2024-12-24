import packetDefs
import ctypes
import libscrc

class processHumidityData():
    def __init__(self,
                 debug=False):
        self.debug        = debug

    def humidityDataPacket(self,packet):

        rtn = False
        humidityInfoData = None

        HABPacketHumidityInfoData = packetDefs.HABPacketHumidityInfoDataType()
        ctypes.memmove(ctypes.pointer(HABPacketHumidityInfoData), packet, ctypes.sizeof(HABPacketHumidityInfoData))
        tempLen =  ctypes.sizeof(HABPacketHumidityInfoData ) - packetDefs.NPAR - packetDefs.CRC16_LEN
        crcByteArray = bytes(HABPacketHumidityInfoData )
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        if(HABPacketHumidityInfoData .crc16 == crc16):
            rtn = True
            humidityInfoData = "{:.1f}RH".format(HABPacketHumidityInfoData.humidityInfoData)
            if(self.debug):
                print(humidityInfoData)

        return rtn,humidityInfoData