from Globals import *
from pattern import Pattern
from GraphicalInterface import *
import wx

class View:

    def __init__(self, controller):
        self.controller = controller
        
        # Create an instance of our customized Frame class - the GUI. (this is the view)
        self.mainWindow = MainWindow(self.controller, "x0xb0x c0ntr0l")
        self.currentPattern = None

    def initialize(self):
        pass

    def destroy(self):
        pass


    ##
    #
    # MODEL --> VIEW PROTOCOL
    #
    ############################



    #
    # True means the serial port is connected, false if it is not.
    #
    def updateSerialStatus(self, state):
        try:
            if state == TRUE:
                self.mainWindow.statusBar.SetStatusText("Serial Port: Connected", 1)
            else:
                self.mainWindow.statusBar.SetStatusText("Serial Port: Disconnected", 1)
        except Exception, e:
            print 'Exception occured: ' + str(e)
            
    def updateSelectedSerialPort(self, name):
        menuId = self.mainWindow.portMenu.FindItem(name)
        if menuId != wx.NOT_FOUND:
            self.mainWindow.portMenu.Check(menuId, True)

    def updateSerialPortNames(self, names):
        for item in self.mainWindow.portMenu.GetMenuItems():
            self.mainWindow.portMenu.Destroy(item)

        for i in range(len(names)):
            self.mainWindow.portMenu.Append(ID_SERIAL_PORT + i, names[i], kind = wx.ITEM_RADIO)

    def updateCurrentPattern(self, pattern):
        self.mainWindow.patternEditGrid.update(pattern)
    
    def updateStatusText(self, string):
        try:
            self.mainWindow.statusBar.SetStatusText(string, 0)
        except Exception, e:
            print 'Exception occured: ' + str(e)

    def displayModalStatusError(self, string):
        print string
        dlg = wx.MessageDialog(self.mainWindow, string, 'x0xb0x c0ntr0l', wx.OK | wx.ICON_INFORMATION) 
        dlg.ShowModal() 
        dlg.Destroy()

    def updateTempo(self, tempo):
        self.mainWindow.tempoText.SetValue(str(tempo))
        self.mainWindow.tempoSlider.SetValue(tempo)
