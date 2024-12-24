
class searcher():
    def __init__(self,
                 searchPattern,
                 debug=False):

        self.searchPattern = searchPattern
        self.debug    = debug
        self.buffer   = []  

    def reset(self):
        self.buffer   = []

    def add(self,bit):
        if(self.buffer != [] and len(self.buffer) == len(self.searchPattern)):
            temp = self.buffer.pop(0)
        self.buffer.append(bit)

    def detected(self):
        rtn = False
        if(self.debug):
            print("Buffer")
            print(self.buffer)
            print("searchPattern")
            print(self.searchPattern)
        if(self.buffer == self.searchPattern):
            rtn = True
        return rtn
