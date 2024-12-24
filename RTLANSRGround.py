import os
import sys
import platform
import time
import queue
import asyncio
import rtlsdr
import configparser

sys.path.append('common')
import FSKDemodulator
import FSKDecoder
import processPayload
import webSocketClientProc
import udpLocationProc
import ftpClientProc
import dataLogger
  
async def main():
    is_windows = any(platform.win32_ver())
    
    sampleQueue      = asyncio.Queue()
    decoderQueue     = asyncio.Queue()
    payloadQueue     = asyncio.Queue() 
    webClientQueue   = queue.Queue(10*1024)
    ftpClientQueue   = queue.Queue(1)
    udpLocationQueue = queue.Queue(10*1024)
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    freq  = int(config.get('modem', 'freq'))
    print("Freq: " + str(freq))
    offset  = int(config.get('modem', 'offset'))
    freq = freq + offset
    Rs    = int(config.get('modem', 'bps'))
    biasT = config.get('modem', 'biasT')

    P           = 10
    Fs          = Rs * P
    scaler      = 20
    M           = 2
    Nsym        = 64
    sample_rate = Fs * scaler
    
    sdr             = rtlsdr.RtlSdr()
    print("Sample Rate = " + str(sample_rate))
    sdr.sample_rate = sample_rate 
    sdr.center_freq = freq
    sdr.gain        = sdr.DEFAULT_GAIN
    sdr.bandwidth   = 25000
    if(biasT == "On"):
        sdr.set_bias_tee(True)
    else:
        sdr.set_bias_tee(False)
    
    GWhost = config.get('network', 'gwIPaddress')
    GWport = int(config.get('network', 'gwPort'))
    GWId = int(config.get('gateway', 'gwID'))

    locationEnabled = config.get('location', 'enabled')
    locationHost    = config.get('location', 'host')
    locationPort    = int(config.get('location', 'port'))    
    
    ftpPort = int(config.get('network', 'gwFTPport'))
    userName = "ansr"
    password = "ansr"
    #userName = "sonde"
    #password = "sonde"

               
    if(is_windows):
        dataLoggerDir = os.getcwd() + "\\logs"
        dataLoggerPath = dataLoggerDir + "\\flightdata.txt"
    else:
        dataLoggerDir = os.getcwd() + "/logs" 
        dataLoggerPath = dataLoggerDir + "/flightdata.txt"
    dataLoggerObj = dataLogger.dataLogger(dataLoggerDir,dataLoggerPath)
    rtn = dataLoggerObj.START()
    rtn = dataLoggerObj.OPEN()  
        
    if(is_windows):
        imageFileDir = dataLoggerDir + "\\images"
    else:
        imageFileDir = dataLoggerDir + "/images"
        
    if os.path.exists(imageFileDir) == False:
        os.mkdir(imageFileDir)
        
    if(is_windows):
        imageSeqFileDir = dataLoggerDir + "\\imageSeq"
    else:
        imageSeqFileDir = dataLoggerDir + "/imageSeq"
        
    if os.path.exists(imageSeqFileDir) == False:
        os.mkdir(imageSeqFileDir)
    

    webSocketClientProcObj = webSocketClientProc.webSocketClientProc(GWhost,GWport,webClientQueue,GWId)
    webSocketClientProcObj.START()
    
    udpLocationProcObj = udpLocationProc.udpLocationProc(locationHost,locationPort, udpLocationQueue)
    if(locationEnabled == "True"):
        udpLocationProcObj.START() 
            
    ftpClientProcObj = ftpClientProc.ftpClientProc(GWhost,ftpPort,userName,password,ftpClientQueue,imageSeqFileDir,is_windows)
    ftpClientProcObj.START() 
        
    processPayloadObj  = processPayload.processPayload(payloadQueue,webClientQueue,udpLocationQueue,ftpClientQueue,imageFileDir,imageSeqFileDir,dataLoggerObj,GWId,is_windows=is_windows)
    
    FSKDemodulatorObj  = FSKDemodulator.FSKDemodulator(sdr,sampleQueue,decoderQueue,scaler)
    FSKDemodulatorObj.initialize(Fs,Rs,M,P,Nsym,is_windows)
    
    FSKDecoderObj  = FSKDecoder.FSKDecoder(decoderQueue,payloadQueue) 
               
    processPayloadTask = asyncio.create_task(processPayloadObj.processPayloadLoopFunc())
    decoderTask        = asyncio.create_task(FSKDecoderObj.decoderLoopFunc())
    demodulatorTask    = asyncio.create_task(FSKDemodulatorObj.demodulatorLoopFunc())
    sampleTask         = asyncio.create_task(FSKDemodulatorObj.sampleLoopFunc()) 

    try:
        while(True):
            await asyncio.sleep(1)
            #raise KeyboardInterrupt
    except:
        print("Shutting Down")

    await processPayloadObj.STOP()
    await FSKDecoderObj.STOP()
    
    sdr.cancel_read_async()
    await FSKDemodulatorObj.STOP()

    webSocketClientProcObj.STOP()
    ftpClientProcObj.STOP()
    dataLoggerObj.CLOSE()  

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except rtlsdr.rtlsdr.LibUSBError as ex:
        print(ex)
    except:
        pass

    print("**** Ending RTLANSR Ground ******")
