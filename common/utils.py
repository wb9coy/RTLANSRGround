def getImageFileName(imageFileID):
    fName = 'image' + '{:0>3}'.format(str(imageFileID)) + ".jpg"
    
    return fName

def getImageSeqFileName(imageFileID,gwID):
    fName = 'image' + '{:0>3}'.format(str(imageFileID)) + "GW_" + str(gwID) + ".seq"
    
    return fName
        
def getJpegPathName(imageFileDir,imageFileID,is_windows):
    fName = getImageFileName(imageFileID)

    if(is_windows):
        pathName = imageFileDir + "\\" + fName
    else:
        pathName = imageFileDir + "/" + fName
        
    return pathName

def getImageSeqFilePathName(imageSeqFileDir,imageSeqFileID,gwID,is_windows):
    fName = getImageSeqFileName(imageSeqFileID,gwID )

    if(is_windows):
        pathName = imageSeqFileDir + "\\" + fName
    else:
        pathName = imageSeqFileDir + "/" + fName
        
    return pathName