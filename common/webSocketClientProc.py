import threading
import time
import ctypes
import packetDefs
from websocket import create_connection

class webSocketClientProc():
    def __init__(self,
                 host,
                 port,
                 webClientQueue,
                 GWId,
                 debug=False):

        self.host            = host
        self.port            = port 
        self.webClientQueue  = webClientQueue
        self.GWId            = GWId
        self.runable         = True
        self.webClientThread = None
        self.pingThread      = None
        self.ws              = None
        self.timeout         = 5
        self.debug           = debug
     
    def join(self):
        threading.Thread.join(self.webClientThread, self.timeout)
        threading.Thread.join(self.pingThread, self.timeout)

    def CONNECT(self):
        rtn = True

        if(self.debug):
            websocket.enableTrace(True)
            
        uri = "ws://" + self.host + ":" + str(self.port)
            
        try:
            self.ws = create_connection(uri)
        except Exception as e:
            rtn = False
            print(e)
        
        return rtn

    def START(self):

        rtn = True
        self.webClientThread = threading.Thread(target=self.webSocletClientThreadFunction)
        self.webClientThread.start()
        time.sleep(1)
    
        if(self.runable):
            self.pingThread = threading.Thread(target=self.pingThreadFunction)
            self.pingThread.start()
            
        return rtn 

    def STOP(self):
        self.runable = False
        self.webClientQueue.put(b'0x0')
        self.join()
        
    def webSocletClientThreadFunction(self):
        print("**** Starting Web Client ******")
        webHABPacketData =  packetDefs.webHABPacketDataType()
        connected        = False
        
        while self.runable:
            while(connected == False):
                connected = self.CONNECT()
                if(connected):
                    print("**** Connected to Websocket Server ****** " + self.host)
                else:
                    time.sleep(10)
            
            webHABPacketData = self.webClientQueue.get()
            if(self.runable):
                try:
                    self.ws.send_binary(webHABPacketData)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}") 
                    connected = False
                    
                if(self.debug):
                    for indx in range(webHABPacketData.webDataLen):
                        print(chr(webHABPacketData.webData[indx]))                   

        print("**** Ending Web Client ******")
        
    def pingThreadFunction(self):
        webHABPacketData =  packetDefs.webHABPacketDataType()
        while self.runable:
            for counter in range(40):
                if(self.runable):
                    time.sleep(.25)
                    
            if(self.runable):
                msg = "$PING_GW" + str(self.GWId)
                msgBytes = bytes(msg, 'utf-8')
                #webHABPacketData.packetType = packetDefs.PING
                #webHABPacketData.webDataLen = len(msg)

                #for indx in range(packetDefs.MAX_WEB_BUF_LEN):
                    #webHABPacketData.webData[indx] = 0x00
                    
                #ctypes.memmove(ctypes.pointer(webHABPacketData.webData), msgBytes, webHABPacketData.webDataLen)          
                    
                self.webClientQueue.put(msgBytes)
        print("**** Ending Ping Thread ******")
                