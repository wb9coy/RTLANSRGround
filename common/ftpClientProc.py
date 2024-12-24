import threading
import time
import ftplib
import utils

class ftpClientProc():
    def __init__(self,
                 host,
                 port,
                 userName,
                 password,
                 ftpClientQueue,
                 imageSeqFileDir,
                 is_windows,
                 debug=False):

        self._host             = host
        self._port             = port
        self._userName         = userName
        self._password         = password
        self._ftpClientQueue   = ftpClientQueue
        self._imageSeqFileDir  = imageSeqFileDir
        self._is_windows       = is_windows
        self._debug            = debug
        
        self._runable          = True
        self._ftpClientThread  = None
        self._ftp              = ftplib.FTP()
        self._timeout          = 5

     
    def join(self):
        threading.Thread.join(self._ftpClientThread, self._timeout)
        
    def CONNECT(self):
        rtn = True
        
        try:
            self._ftp.connect(self._host, self._port)
            self._ftp.set_pasv(True)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            rtn = False
            
        if(rtn):
            try:
                self._ftp.login(user=self._userName, passwd =  self._password) 
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                print("Check FTP user name and password")
                rtn = False        
        
        return rtn

    def START(self):

        rtn = True
           
        self._ftpClientThread = threading.Thread(target=self._ftpClientThreadFunction)
        self._ftpClientThread.start()
        time.sleep(1)
        
        return rtn 

    def STOP(self):
        self._runable = False
        self._ftp.quit()
        time.sleep(1) 
        self._ftpClientQueue.put(b'0x0')
        self.join()
        
    def _ftpClientThreadFunction(self):
        print("**** Starting FTP Client ******")
        connected        = False
        
        while self._runable:      
            ftpFileData = self._ftpClientQueue.get()
            connected = self.CONNECT()
            if(connected):
                print("**** Connected to FTP Server ****** " + self._host)     
                imageSeqFilePathName = utils.getImageSeqFilePathName(self._imageSeqFileDir,ftpFileData[0], ftpFileData[1], self._is_windows)
                imageSeqFileName = utils.getImageSeqFileName(ftpFileData[0],ftpFileData[1])
                try:
                    self._ftp.storbinary('STOR '+imageSeqFileName, open(imageSeqFilePathName, 'rb'))
                    print("FTP Transfer " +imageSeqFilePathName)
                    ftpReply = self._ftp.quit()
                    if(self._debug):
                        print(ftpReply)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
            
        print("**** Ending FTP Client ******")