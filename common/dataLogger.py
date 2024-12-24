import os
import queue
import threading
import time
from datetime import datetime


class dataLogger():
    
    def __init__(self,
                 dataLoggerDir,
                 dataLoggerPath,
                 debug=False):
        
        self.logQ             = queue.Queue(1024*10)
        self.runable          = True
        self.dataLoggerThread = None
        self.dataLoggerDir    = dataLoggerDir
        self.dataLoggerPath   = dataLoggerPath
        self.fileId           = None
        self.debug            = True 
        
        if os.path.exists(self.dataLoggerDir) == False:
            os.mkdir(self.dataLoggerDir) 
            
    def join(self, timeout=None):
        if(self.dataLoggerThread != None):
            threading.Thread.join(self.dataLoggerThread, timeout)        
        
    def START(self):
        
        print("**** Starting Data Logger ******")
        rtn = True
        self.dataLoggerThread = threading.Thread(target=self.dataLoggerThreadFunc)
        if(self.dataLoggerThread != None):
            self.dataLoggerThread.start()
            time.sleep(1)
        else:
            rtn = False
        
        return rtn 

    def OPEN(self):

        rtn = True
        
        try:
            self.fileId = open(self.dataLoggerPath,"a")
        except OSError as e:
            print(e)
            rtn = False
            
        return rtn     

    def CLOSE(self):
        while(self.logQ.empty() == False):
            pass
        self.runable = False
        self.logQ.put("*** END LOG ***")
        self.join()
        self.fileId.close()
        return True

    def LOG(self, msg):
        rtn = True
        
        try:
            if(msg != None):
                self.logQ.put(msg)
        except queue.Full as e:
            print(str(e))
            rtn = False
            
        return rtn
                            
    def dataLoggerThreadFunc(self):
        
        while(self.runable):
            logMsg = self.logQ.get(True)
            now = datetime.now()
            t = now.strftime("%Y:%m:%d %H:%M:%S")
            temp = t + logMsg
            temp = temp.replace("\r\n", "")
            temp = temp.replace("\0", "")
            self.fileId.write(temp+"\n")
            self.fileId.flush()
    
        print("**** Ending Data Logger Thread ******")        
