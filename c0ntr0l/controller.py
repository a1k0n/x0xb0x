from Globals import *
import wx

class Controller:

    def __init__(self, app):
        self.app = app
        self.LoadConfiguration()
        pass

    def destroy(self):
        self.SaveConfiguration()
                

    def setView(self, view):
        self.view = view

    def setModel(self, model):
        self.model = model

    def quitApp(self):
        self.SaveConfiguration()
        self.app.ExitMainLoop()

    #
    # Load and save the preferences dictionary for this application.
    # These preferences are automatically read and saved when the application
    # opens or closes using the procedures below.
    #
    def LoadConfiguration(self):
        self.cfgFile = wx.Config(APP_NAME)
        wx.Config.Set(self.cfgFile)
    
    def SaveConfiguration(self):
        self.cfgFile.Flush()

    def GetConfigValue(self, key):
        # print 'Reading ' + key + ' : ' + self.cfgFile.Read(key)
        return self.cfgFile.Read(key)

    def SetConfigValue(self, key, value):
        # print 'Writing ' + key + ' : ' + value
        self.cfgFile.Write(key, value)


    ##
    #
    # VIEW --> MODEL PROTOCOL
    #
    ##

    def openSerialPort(self):
        return self.model.openSerialPort()
    
    def closeSerialPort(self):
        return self.model.closeSerialPort()
    
    def selectSerialPort(self, port):
        return self.model.selectSerialPort(port)
    
    def writepattern(self, pattern, bank, loc):
        pass

    def readPattern(self, bank, loc):
        pass

    def backupAllPatterns(self, tofile):
        pass
    
    def restoreAllPatterns(self, fromfile):
        pass
    
    def sendRunStop(self):
        return self.model.runTest()
        
    def setCurrentBank(self, bank):
        pass
    
    def setCurrentLoc(self, loc):
        pass
    
    def setTempo(self, tempo):
        pass
    
    def setSync(self, sync):
        pass

    def uploadHexfile(self, filename):
        return self.model.uploadHexfile(filename)

    ##
    #
    # MODEL --> VIEW PROTOCOL
    #
    ##
    def updateSerialStatus(self, state):
        return self.view.updateSerialStatus(state)
    
    def updateSelectedSerialPort(self, name):
        return self.view.updateSelectedSerialPort(name)
        
    def updateSerialPortNames(self, names):
        return self.view.updateSerialPortNames(names)
    
    def updateCurrentPattern(self, pattern):
        return self.view.updateCurrentPattern(pattern)
    
    def updateLoc(self, loc):
        pass
    
    def updateBank(self, bank):
        pass
    
    def updateTempo(self, tempo):
        pass
    
    def updateSync(self, sync):
        pass

    def updateStatusText(self, string):
        return self.view.updateStatusText(string)

    def displayModalStatusError(self, string):
        return self.view.displayModalStatusError(string)


        
