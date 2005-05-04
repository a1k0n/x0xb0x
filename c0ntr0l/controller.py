
class Controller:

    def __init__(self):
        pass

    def setView(self, view):
        self.view = view

    def setModel(self, model):
        self.model = model


    ##
    #
    # VIEW --> MODEL PROTOCOL
    #
    ##
    def openSerialPort(self):  # Perhaps these happen automatically??
        pass
    
    def closeSerialPort(self):
        pass
    
    def selectSerialPort(self, port):
        pass
    
    def writepattern(self, pattern, bank, loc):
        pass

    def readPattern(self, bank, loc):
        pass

    def backupAllPatterns(self, tofile):
        pass
    
    def restoreAllPatterns(self, fromfile):
        pass
    
    def sendRunStop(self):
        self.model.runTest()
        
    def setCurrentBank(self, bank):
        pass
    
    def setCurrentLoc(self, loc):
        pass
    
    def setTempo(self, tempo):
        pass
    
    def setSync(self, sync):
        pass

    def uploadHexfile(self, filename):
        self.model.uploadHexfile(filename)

    ##
    #
    # MODEL --> VIEW PROTOCOL
    #
    ##
    def updateSerialStatus(self, state):
        pass
    
    def updateSelectedSerialPort(self, port):
        pass
    
    def updateSerialPortName(self, port, name):
        pass
    
    def updateCurrentPattern(self, pattern):
        self.view.updateCurrentPattern(pattern)
    
    def updateLoc(self, loc):
        pass
    
    def updateBank(self, bank):
        pass
    
    def updateTempo(self, tempo):
        pass
    
    def updateSync(self, sync):
        pass

    def updateStatusText(self, string):
        self.view.updateStatusText(string)
