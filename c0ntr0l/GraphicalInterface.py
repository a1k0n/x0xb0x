#
# Josh Lifton and Michael Broxton
# MIT Media Lab
# Copyright (c) 2002-2004. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

#----------------------------------------------------------------------------
# Name:         Interface.py
#
# Purpose:      The graphical front end (the view in the model-view-controller model).
#               This file contains routines that define the basic GUI layout of the 
#               This includes menus, the main window, the buttons and controls,
#               and the status bar. 
#
# Author:       Michael Broxton 
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2004 by MIT Media Laboratory
#----------------------------------------------------------------------------


#
# Import all of the wxPython GUI package, the PushpinDebugger Globals, and
# the sys package.
#

from Globals import *
from wxPython.wx import *
import wx.grid

from PatternEditGrid import PatternEditGrid
from PatternPlayGrid import PatternPlayGrid

DEFAULT_MAINWINDOW_SIZE = (600, 542)
DEFAULT_MAINWINDOW_POS = (150, 150)  # Default position

#
# ID Definitions for the event handling system.
#
ID_MAIN_WINDOW = wxNewId()

ID_FILE_EXIT = wxNewId() 
ID_FILE_ABOUT = wxNewId()
ID_X0XB0X_UPLOAD_FIRMWARE = wxNewId()
ID_X0XB0X_DUMP_EEPROM = wxNewId()
ID_X0XB0X_RESTORE_EEPROM = wxNewId()
ID_X0XB0X_RECONNECT_SERIAL = wxNewId()

ID_SERIAL_PORT1 = wxNewId()
ID_SERIAL_PORT2 = wxNewId()
ID_SERIAL_PORT3 = wxNewId()
ID_SERIAL_PORT4 = wxNewId()

ID_RUNSTOP_BUTTON = wxNewId()

## Create a new frame class, derived from the wxPython Frame.  This is where
## the main parts of the GUI are set up -- Specifically, the menus, toolbar
## and status window. 
##
class MainWindow(wxFrame):
    
    def __init__(self, controller, title, style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE):
        #
        # First, make a local pointer to the controller class so that we can refer to it later
        # when be begin connection actions.
        #
        self.controller = controller

        #
        # Read the previously saved window location, if any.
        #
        try:
            xloc = int(self.controller.GetConfigValue('mainwindowxloc'))
            yloc = int(self.controller.GetConfigValue('mainwindowyloc'))
            position = (xloc,yloc)
        except Exception, e:
            position = DEFAULT_MAINWINDOW_POS
        
        #
        # Call the base class' __init__ method to create the frame
        #
        wxFrame.__init__(self, NULL, ID_MAIN_WINDOW, title, size = DEFAULT_MAINWINDOW_SIZE,
                         pos = position,
                         style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE|wxMAXIMIZE)

        EVT_CLOSE(self, self.OnCloseWindow)


        #
        # This line is critical for reading in image data from files. (And it took
        # me an entire afternoon one day to find it in the documentation...)  Don't
        # let this happen to you, kids.
        #
        wxInitAllImageHandlers()

        #
        # Initialize various components of the GUI
        #
        self.SetupMenubar()
        self.SetupStatusbar()
        self.SetupMainFrame()

        #
        # Once everything has been set up, show the frame.
        #
        self.Show(true)


    #---------------------------------------------------------------------
    #
    # Set up a the main viewing area of the application.
    #
    # This is where all the dirty GUI work is done.
    def SetupMainFrame(self):
        logo = wxStaticText(self, -1, "x0xb0x c0ntr0l", (378, 20))
        font = wxFont(24, wxTELETYPE, wxNORMAL, wxNORMAL, faceName = "Courier")
        logo.SetFont(font)
        logo.SetSize(logo.GetBestSize())

        #
        # Create the basic framework for the window
        #
        divider1 = wxStaticLine(self, -1, pos = (15,55), size = (569,1), style = wxLI_HORIZONTAL)
        divider2 = wxStaticLine(self, -1, pos = (15,277), size = (569,1), style = wxLI_HORIZONTAL)
        #divider3 = wxStaticLine(self, -1, pos = (15,414), size = (569,1), style = wxLI_HORIZONTAL)
        
        label1 = wxStaticText(self, -1, "Pattern Edit", (20, 64))
        label2 = wxStaticText(self, -1, "Pattern Play", (20, 286))
        #label3 = wxStaticText(self, -1, "Global Parameters", (20, 423))

        #
        # Pattern Edit Section
        #
        pe_font = wxFont(11, wxDEFAULT, wxNORMAL, wxNORMAL)
        pe_label1 = wxStaticText(self, -1, "Bank:", (36, 228), style = wxALIGN_RIGHT)
        pe_label1.SetFont(pe_font)
        pe_label1.SetSize(pe_label1.GetBestSize())

        pe_label2 = wxStaticText(self, -1, "Location:", (18, 253), style = wxALIGN_RIGHT)
        pe_label2.SetFont(pe_font)
        pe_label2.SetSize(pe_label2.GetBestSize())

#        pe_label3 = wxStaticText(self, -1, "Backup:", (461, 226), style = wxALIGN_RIGHT)
#        pe_label3.SetSize(pe_label3.GetBestSize())

        pe_text1 = wxTextCtrl(self, -1, "1", (71, 225), (39,19), style = (wxTE_PROCESS_ENTER))
        pe_text2 = wxTextCtrl(self, -1, "1", (71, 250), (39,19), style = (wxTE_PROCESS_ENTER))

        pe_button1 = wxButton(self, -1, "Write", (118, 226), (66, 17))
        pe_button2 = wxButton(self, -1, "Read", (118, 251), (66, 17))
#        pe_button3 = wxButton(self, -1, "Dump", (518, 226), (66, 17))
#        pe_button4 = wxButton(self, -1, "Restore", (518, 251), (66, 17))


        #
        # Pattern Edit Grid
        #
        self.patternEditGrid = PatternEditGrid(self)
        
        for i in range(1,17):
            wxStaticText(self, -1, str(i), (82 + (i-1)*507/16, 111))
            
        wxStaticText(self, -1, "Notes:", (24, 138))
        wxStaticText(self, -1, "Lengths:", (11, 164))
        wxStaticText(self, -1, "Effects:", (20, 190))

        #
        # Pattern Play Grid
        #
        self.patternPlayGrid = PatternPlayGrid(self)

        for i in range(1,9):
            wxStaticText(self, -1, str(i), (96 + (i-1)*515/8, 318))
        wxStaticText(self, -1, "Pattern:", (17, 362))


        #
        # Other controls and buttons in the Pattern Play section
        #
        pp_button1 = wxButton(self, ID_RUNSTOP_BUTTON, "R/S", (75, 413), (66, 17))
        pp_button1 = wxButton(self, -1, "Load", (518, 413), (66, 17))

        EVT_BUTTON(self, ID_RUNSTOP_BUTTON, self.HandleButtonAction)

        pp_label1 = wxStaticText(self, -1, "Bank:", (436, 415), style = wxALIGN_RIGHT)
        pp_label1.SetFont(pe_font)
        pp_label1.SetSize(pp_label1.GetBestSize())

        pp_text1 = wxTextCtrl(self, -1, "1", (476,412), (39,19), style = (wxTE_PROCESS_ENTER))

        #
        # Use some sizers to help keep everything in the window nicely proportioned
        # if the window is resized.
        #
        self.sizer = wxBoxSizer(wxVERTICAL)
#        self.sizer.Add(self.splitter, 1, wxEXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)




           
    #---------------------------------------------------------------------
    #
    # Set up a basic menu bar.  
    def SetupMenubar(self):
        menubar = wxMenuBar()
        self.MenuBar = menubar
        
        menu = wxMenu()
        menu.Append(ID_FILE_ABOUT, "About", "About This Program")
        menu.Append(ID_FILE_EXIT, "Quit\tCTRL-Q", "Exit the Program")
        menubar.Append(menu, "File")

        menu = wxMenu()
        menu.Append(ID_X0XB0X_UPLOAD_FIRMWARE, "Upload firmware...\tCTRL-U", "Upload a new .HEX file to the x0xb0x firmware")
        menu.AppendSeparator()
        menu.Append(ID_X0XB0X_DUMP_EEPROM, "Backup EEPROM", "Backup EEPROM to the hard disk")
        menu.Append(ID_X0XB0X_RESTORE_EEPROM, "Restore EEPROM", "Restore EEPROM from a backup on the hard drive")
        menubar.Append(menu, "x0xb0x")


        menu = wxMenu()
        self.portMenu = wx.Menu()
        menu.Append(ID_X0XB0X_RECONNECT_SERIAL, "Reconnect serial port\tCTRL-R")
        menu.AppendMenu(-1, 'Port', self.portMenu)
        menubar.Append(menu, 'Serial')
        
            
        self.SetMenuBar(menubar)

        #
        # Create event bindings for each of the menu options specified above.
        # 
        EVT_MENU(self, ID_FILE_ABOUT, self.HandleMenuAction)
        EVT_MENU(self, ID_FILE_EXIT, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_RECONNECT_SERIAL, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_UPLOAD_FIRMWARE, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_DUMP_EEPROM, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_RESTORE_EEPROM, self.HandleMenuAction)
        EVT_MENU(self, ID_SERIAL_PORT1, self.HandleMenuAction)
        EVT_MENU(self, ID_SERIAL_PORT2, self.HandleMenuAction)
        EVT_MENU(self, ID_SERIAL_PORT3, self.HandleMenuAction)
        EVT_MENU(self, ID_SERIAL_PORT4, self.HandleMenuAction)

    # --------------------------------------------------------------------
    #
    # Build the Status Bar
    #
    def SetupStatusbar(self):
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount( 2 )

        # Set the first field to variable length, second field to fixed.  
        self.statusBar.SetStatusWidths( [-1, 160] )

        self.statusBar.SetStatusText( "Welcome to the x0xb0x c0ntr0l!!", 0 )
        self.statusBar.SetStatusText( "",1)

    #---------------------------------------------------------------------
    #
    # The about box dialog.
    #
    def AboutBox(self):
        aboutString = ('(c) 2005 Michael Broxton.\n\n' +
                       'Kudos to ladyada and the german for creating a bitchin\' synth!\n')
        dlg = wxMessageDialog(self, aboutString, 'x0xb0x c0ntr0l', wxOK | wxICON_INFORMATION) 
        dlg.ShowModal() 
        dlg.Destroy()



    #
    # This method is called automatically when the CLOSE event is
    # sent to this window.  This message is also sent when the application
    # is going to quit.
    #
    def OnCloseWindow(self, event):
        pos = self.GetPositionTuple()
        self.controller.SetConfigValue('mainwindowxloc', str(pos[0]))
        self.controller.SetConfigValue('mainwindowyloc', str(pos[1]))
        self.Destroy()

#---------------------------------------------------------------------------
# UTILITY CLASSES (classes that are used by the main GUI class above)
#

    #
    # ====================== Actions ============================
    #
    def HandleToolbarAction(self,event):
        #
        # Meme - There may be a bug here -- You would think that you would
        # have to negate the current state of the button to toggle it on or
        # off. Instead, it would appear that if you set the toggle state to
        # its current state, it actually toggles states!
        #
        #        nextState = self.mainWindow.ToolBar.GetToolState(event.GetId())
        #        self.mainWindow.ToolBar.ToggleTool(event.GetId(), nextState)

        pass  # There are currently no toolbar events to handle.
         
    def HandleButtonAction(self,event):
        print 'Button messoge received...'
        if event.GetId() == ID_RUNSTOP_BUTTON:
            self.controller.sendRunStop()
    
    def HandleMenuAction(self, event):
        if event.GetId() == ID_FILE_ABOUT:
            self.AboutBox()

        elif event.GetId() == ID_FILE_EXIT:
            self.Close(true)

        elif event.GetId() == ID_X0XB0X_RECONNECT_SERIAL:
            print "reconnectiong"
            self.controller.closeSerialPort()
            self.controller.openSerialPort()
            
        elif event.GetId() == ID_X0XB0X_UPLOAD_FIRMWARE:
            d = wxFileDialog(self, 'Choose a x0xb0x firmware file', style = wxOPEN)
            d.ShowModal()
            if len(d.GetPath()) != 0:
                try:
                    self.controller.uploadHexfile(d.GetPath())
                except Exception, e:
                    errorDialog = wxMessageDialog(self,
                                                  message = 'The following exception occured while programming the flash memory on the x0xb0x:\n\nException: ' + str(e),
                                                  caption = 'Firmware Programming Error',
                                                  style = wxOK)
                    errorDialog.ShowModal()


        elif event.GetId() == ID_X0XB0X_DUMP_EEPROM:
            #
            # Dump eeprom
            #
            d = wxFileDialog(self, 'Save EEPROM image to...', style = wxSAVE)
            d.ShowModal()
            if len(d.GetPath()) != 0:
                try:
                    self.controller.backupAllPatterns(d.GetPath())
                except Exception, e:
                    errorDialog = wxMessageDialog(self,
                                                  message = 'The following exception occured while programming the flash memory on the x0xb0x:\n\nException: ' + str(e),
                                                  caption = 'EEPROM Backup Error',
                                                  style = wxOK)
                    errorDialog.ShowModal()

        elif event.GetId() == ID_X0XB0X_RESTORE_EEPROM:
            #
            # Retore EEPROM
            #
            d = wxFileDialog(self, 'Choose a x0xb0x EEPROM image file', style = wxOPEN)
            d.ShowModal()
            if len(d.GetPath()) != 0:
                try:
                    self.controller.restoreAllPatterns(d.GetPath())
                except Exception, e:
                    errorDialog = wxMessageDialog(self,
                                                  message = 'The following exception occured while programming the flash memory on the x0xb0x:\n\nException: ' + str(e),
                                                  caption = 'EEPROM Restore Error',
                                                  style = wxOK)
                    errorDialog.ShowModal()

        elif event.GetId() == ID_SERIAL_PORT1:
            self.controller.selectSerialPort(self.portMenu.GetLabel(ID_SERIAL_PORT1))

        elif event.GetId() == ID_SERIAL_PORT2:
            self.controller.selectSerialPort(self.portMenu.GetLabel(ID_SERIAL_PORT2))

        elif event.GetId() == ID_SERIAL_PORT3:
            self.controller.selectSerialPort(self.portMenu.GetLabel(ID_SERIAL_PORT3))

        elif event.GetId() == ID_SERIAL_PORT4:
            self.controller.selectSerialPort(self.portMenu.GetLabel(ID_SERIAL_PORT4))

