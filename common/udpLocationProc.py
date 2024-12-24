import threading
import time
import socket

class udpLocationProc():
    def __init__(self,
                 host,
                 port,
                 udpLocationQueue,
                 debug=False):

        self.host            = host
        self.port            = port
        self._udpLocationQueue  = udpLocationQueue
        self._debug          = debug
        
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # enable address reuse
        self._udpLocationThread = threading.Thread(target=self._udpLocationThreadFunction)
        
        self.runable         = True
        self.timeout         = 5

    def _join(self):
        threading.Thread.join(self._udpLocationThread, self.timeout)

    def START(self):

        rtn = True
        
        self._udpLocationThread.start()
        time.sleep(1)

        return rtn 

    def STOP(self):
        self._runable = False
        self._join()

    def _udpLocationThreadFunction(self):
        print("**** Starting UDP location proccess ******")

        while self.runable:
            try:
                locData = self._udpLocationQueue.get(timeout=1)
                self._sock.sendto(bytes(locData, 'utf-8'), (self.host, self.port))         
            except :
                pass
                
        print("**** Ending UDP location proccess ******")
