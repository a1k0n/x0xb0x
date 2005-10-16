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
        try:
            # print 'Reading ' + key + ' : ' + self.cfgFile.Read(key)
            return self.cfgFile.Read(key)
        except Exception, e:
            raise ConfigException("Could not load config value: " + key + ".")

    def SetConfigValue(self, key, value):
        try:
            # print 'Writing ' + key + ' : ' + value
            self.cfgFile.Write(key, value)
        except Exception, e:
            raise ConfigException("Could not write config value: " + key + ".")
            


    ##
    #
    # VIEW --> MODEL PROTOCOL
    #
    ##

    def sendPing(self):
        return self.model.runTest()

    def openSerialPort(self):
        return self.model.openSerialPort()
    
    def closeSerialPort(self):
        return self.model.closeSerialPort()
    
    def selectSerialPort(self, port):
        return self.model.selectSerialPort(port)
    
    def connectSerialPort(self):
        return self.model.connectSerialPort()
    
    def writePattern(self, pattern, bank, loc):
        return self.model.writePattern(pattern, bank, loc)

    def readPattern(self, bank, loc):
        return self.model.readPattern(bank, loc)

    def playPattern(self, pattern):
        return self.model.playPattern(pattern)
            
    def backupAllPatterns(self, tofile):
        return self.model.backupAllPatterns(tofile)
    
    def restoreAllPatterns(self, fromFile):
        return self.model.restoreAllPatterns(fromFile)

    def eraseAllPatterns(self):
        return self.model.eraseAllPatterns()
    
    def sendRunStop(self):
        return self.model.sendToggleSequencerMessage()

    def setCurrentBank(self, bank):
        pass
    
    def setCurrentLoc(self, loc):
        pass
    
    def setTempo(self, tempo):
        return self.model.setTempo(tempo)

    def readTempo(self):
        return self.model.readTempo()

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
        return self.view.updateTempo(tempo)
    
    def updateSync(self, sync):
        pass

    def updateStatusText(self, string):
        return self.view.updateStatusText(string)

    def displayModalStatusError(self, string):
        return self.view.displayModalStatusError(string)


    
