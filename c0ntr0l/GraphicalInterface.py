
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


DEFAULT_MAINWINDOW_SIZE = (600, 556)
DEFAULT_MAINWINDOW_POS = (150, 150)     # Default position


#
# Widget ID definitions for the event handling system.
#
ID_MAIN_WINDOW = wxNewId()

ID_FILE_EXIT = wxNewId() 
ID_FILE_ABOUT = wxNewId()
ID_X0XB0X_UPLOAD_FIRMWARE = wxNewId()
ID_X0XB0X_DUMP_EEPROM = wxNewId()
ID_X0XB0X_RESTORE_EEPROM = wxNewId()
ID_X0XB0X_ERASE_EEPROM = wxNewId()
ID_X0XB0X_RECONNECT_SERIAL = wxNewId()
ID_X0XB0X_PING = wxNewId()

ID_SERIAL_PORT = 10000


ID_PE_LOC_TEXT = wxNewId()
ID_PE_BANK_TEXT = wxNewId()
ID_LENGTH_TEXT = wxNewId()
ID_TEMPO_TEXT = wxNewId()
ID_RUNSTOP_BUTTON = wxNewId()
ID_SAVE_PATTERN_BUTTON = wxNewId()
ID_LOAD_PATTERN_BUTTON = wxNewId()
ID_PP_LOAD_BANK_BUTTON = wxNewId()
ID_SYNC_CHOICE = wxNewId()

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

        self.currentBank = 0
        self.currentLoc = 0


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

        #
        # ==== The Logo and basic windw framework (labels and dividers) ====
        #
        logo = wxStaticText(self, -1, "x0xb0x c0ntr0l", (378, 20))
        font = wxFont(24, wxTELETYPE, wxNORMAL, wxNORMAL, faceName = "Courier")
        logo.SetFont(font)
        logo.SetSize(logo.GetBestSize())

        divider1 = wxStaticLine(self, -1, pos = (15,55), size = (569,1), style = wxLI_HORIZONTAL)
        divider2 = wxStaticLine(self, -1, pos = (15,277), size = (569,1), style = wxLI_HORIZONTAL)
        divider3 = wxStaticLine(self, -1, pos = (15,442), size = (569,1), style = wxLI_HORIZONTAL)
        
        label1 = wxStaticText(self, -1, "Pattern Edit", (20, 64))
        label2 = wxStaticText(self, -1, "Pattern Play", (20, 286))
        label3 = wxStaticText(self, -1, "Global Parameters", (20, 450))

        #
        # ==== Pattern Edit Section ====
        #

        font = wxFont(11, wxDEFAULT, wxNORMAL, wxNORMAL)

        # Bank select control
        pe_label1 = wxStaticText(self, -1, "Bank:", (36, 228), style = wxALIGN_RIGHT)
        pe_label1.SetFont(font)
        pe_label1.SetSize(pe_label1.GetBestSize())

        bankStrings = []
        for i in range(1, NUMBER_OF_BANKS + 1):
            bankStrings.append(str(i))
        self.pe_bankText = wxChoice(self, ID_PE_BANK_TEXT,
                                      (71, 225), (58,19),
                                      choices = bankStrings)
        self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.pe_bankText)
        
        # Location Select Control
        pe_label2 = wxStaticText(self, -1, "Location:", (18, 253), style = wxALIGN_RIGHT)
        pe_label2.SetFont(font)
        pe_label2.SetSize(pe_label2.GetBestSize())

        self.pe_locText = wxChoice(self, ID_PE_LOC_TEXT, 
                                   (71, 250), (59,19),
                                   choices = bankStrings)
        self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.pe_locText)
        
        # Save button
        self.pe_SaveButton = wxButton(self, ID_SAVE_PATTERN_BUTTON, "Save Pattern", (484, 251), (100, 17))
        self.pe_SaveButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, self.pe_SaveButton)


        # Pattern length control
        pe_label2 = wxStaticText(self, -1, "Pattern Length:", (450, 228), style = wxALIGN_RIGHT)
        pe_label2.SetFont(font)
        pe_label2.SetSize(pe_label2.GetBestSize())


        textValidator = TextValidator(map(str, range(1, NOTES_IN_PATTERN + 1)))        
        self.lengthText = wxTextCtrl(self, ID_LENGTH_TEXT, str(NOTES_IN_PATTERN), (542, 225), (39,19),
                                     style = (wxTE_PROCESS_ENTER),
                                     validator = textValidator)
        self.lengthText.Disable()
        self.Bind(wx.EVT_TEXT_ENTER, self.HandleTextEnterEvent)

        
#        EVT_TEXT(self.lengthText, self.HandleKeyAction)
#        EVT_KEY_DOWN(self.lengthText, self.HandleKeyAction)
        
        #
        # Pattern Edit Grid
        #
        self.patternEditGrid = PatternEditGrid(self, (70, 130))
        
        #
        # ==== Pattern Play Section ====
        #
        self.patternPlayGrid = PatternPlayGrid(self)

        for i in range(1,9):
            wxStaticText(self, -1, str(i), (96 + (i-1)*515/8, 318))
        wxStaticText(self, -1, "Pattern:", (17, 362))


        #
        # Other controls and buttons in the Pattern Play section
        #
        pp_button1 = wxButton(self, ID_RUNSTOP_BUTTON, "R/S", (75, 413), (66, 17))
        pp_button2 = wxButton(self, ID_PP_LOAD_BANK_BUTTON, "Load", (518, 413), (66, 17))
        self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, pp_button1)
        self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, pp_button2)
        
        pp_label1 = wxStaticText(self, -1, "Bank:", (436, 415), style = wxALIGN_RIGHT)
        pp_label1.SetFont(font)
        pp_label1.SetSize(pp_label1.GetBestSize())

        textValidator = TextValidator(map(str, range(1, NUMBER_OF_BANKS + 1))) 
        self.pp_bankSelect = wxTextCtrl(self, -1, "1", (476,412), (39,19),
                                        style = (wxTE_PROCESS_ENTER),
                                        validator = textValidator)


        # 
        # The tempo and sync source controls appear in the very bottom of the
        # window.
        #
        tempoText = wxStaticText(self, -1, "Tempo:", (27, 486), style = wxALIGN_LEFT)
        tempoText.SetFont(font)
        tempoText.SetSize(pe_label2.GetBestSize())

#        textValidator = TextValidator(map(str, range(1, NOTES_IN_PATTERN + 1)))        
        self.tempoText = wxTextCtrl(self, ID_TEMPO_TEXT, '60', (71, 484), (39,19),
                                     style = (wxTE_PROCESS_ENTER))
        self.Bind(wx.EVT_TEXT_ENTER, self.HandleTextEnterEvent)


        syncText = wxStaticText(self, -1, "Select sync mode:", (350, 486), style = wxALIGN_LEFT)
        syncText.SetFont(font)
        syncText.SetSize(syncText.GetBestSize())
        
        syncList = [SYNCMSG_OUT, SYNCMSG_IN_MIDI, SYNCMSG_IN_DIN]
        self.syncChoice = wxChoice(self, ID_SYNC_CHOICE, (454, 484), choices = syncList)
        self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.syncChoice)
        self.syncChoice.SetSelection(0)

        try:
            syncPreference = self.controller.GetConfigValue('syncchoice')
            for i in range(0,len(syncList)):
                if syncPreference == syncList[i]:
                    self.syncChoice.SetSelection(i)
        except ConfigException, e:
            # No preference yet exists for sync source.
            pass

        self.controller.setSync(self.syncChoice.GetString(self.syncChoice.GetSelection()))

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
        menu.AppendSeparator()
        menu.Append(ID_X0XB0X_ERASE_EEPROM, "Erase EEPROM", "Erase the patterns on your x0xb0x.")
        menubar.Append(menu, "x0xb0x")

        menu = wxMenu()
        self.portMenu = wx.Menu()
        menu.Append(ID_X0XB0X_RECONNECT_SERIAL, "Reconnect serial port\tCTRL-R")
        menu.Append(ID_X0XB0X_PING, "Send serial ping\tCTRL-P")
        menu.AppendSeparator()
        menu.AppendMenu(-1, 'Port', self.portMenu)
        menubar.Append(menu, 'Serial')
        
            
        self.SetMenuBar(menubar)

        #
        # Create event bindings for each of the menu options specified above.
        # 
        EVT_MENU(self, ID_FILE_ABOUT, self.HandleMenuAction)
        EVT_MENU(self, ID_FILE_EXIT, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_RECONNECT_SERIAL, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_PING, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_UPLOAD_FIRMWARE, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_DUMP_EEPROM, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_RESTORE_EEPROM, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_ERASE_EEPROM, self.HandleMenuAction)

        # Bind events for 25 potential serial ports.
        for i in range(25):
            EVT_MENU(self, ID_SERIAL_PORT + i, self.HandleMenuAction)


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
    # The about box dialo.g
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
   
    #
    # Returns true if pattern was loaded succesfully, false otherwise.
    #
    def LoadPattern(self):
        if (self.pe_bankText.GetSelection() > -1) and (self.pe_locText.GetSelection() > -1):
            bank = int(self.pe_bankText.GetSelection()) + 1
            loc = int(self.pe_locText.GetSelection()) + 1
            if self.controller.readPattern(bank,loc):
                # Disable the save button until the grid is editted.
                self.pe_SaveButton.Disable()
                self.lengthText.Enable()
                self.currentBank = bank
                self.currentLoc = loc
            else:
                # The user has not yet selected a valid bank/loc combination.
                self.patternEditGrid.SetPatternLength(0)
                self.lengthTextDisable()
                self.pe_SaveButton.Disable()
                self.currentBank = 0
                self.currentLoc = 0
                return False
                
        else:
            # The user has not yet selected a valid bank/loc combination.
            self.controller.updateStatusText("Please select a bank and location")
            self.patternEditGrid.SetPatternLength(0)
            self.lengthText.Disable()
            self.pe_SaveButton.Disable()
            self.currentBank = 0
            self.currentLoc = 0
            return False

    #
    # Return true if the pattern was succesfully saved, false otherwise
    #
    def SavePattern(self):
        if (self.currentBank > 0) and (self.currentLoc > 0):
            return self.controller.writePattern(self.patternEditGrid.getPattern(),
                                                self.currentBank, self.currentLoc)
        else:
            # This exception fires if enter is pressed when the text
            # box is empty.  In this case, warn the user.
            self.controller.displayModalStatusError("Please select a bank and location")
            return False

#---------------------------------------------------------------------------
# UTILITY CLASSES (classes that are used by the main GUI class above)
#

    #
    # ====================== Actions ============================
    #

    def HandleButtonAction(self,event):
        if event.GetId() == ID_SAVE_PATTERN_BUTTON:
            if self.SavePattern():
                self.pe_SaveButton.Disable()
            
        elif event.GetId() == ID_RUNSTOP_BUTTON:
            print "R/S"
            self.controller.sendRunStop()

        elif event.GetId() == ID_PP_LOAD_BANK_BUTTON:
            print "Load Bank"
            self.controller.setCurrentBank(int(self.pp_bankSelect.GetValue()))

    #
    # Event handler for grid updates
    #   
    def OnGridChange(self):
        self.pe_SaveButton.Enable()

    #
    # Handle events generated by dropdown choice menus
    #
    def HandleChoiceAction(self, event):
        if (event.GetId() == ID_PE_BANK_TEXT) or (event.GetId() == ID_PE_LOC_TEXT):
            #
            # If the we have made changes to the current pattern, ask the user
            # whether or not to save changes.
            #
            if self.pe_SaveButton.IsEnabled():
                dlg = wxMessageDialog(self,
                                      message = 'You have made changes to this pattern.  Would you like to save your changes?',
                                      caption = "Save Pattern?",
                                      style = (wxICON_EXCLAMATION | wxYES_NO | wxYES_DEFAULT))
                if dlg.ShowModal() == wxID_YES:
                    if self.SavePattern():
                        # If the pattern can be saved, load the pattern
                        self.LoadPattern()
                else:
                    # The user has decided not to save changes.  Load the next pattern
                    self.LoadPattern()
            else:
                # If the pattern has not been saved, simply load the new pattern
                self.LoadPattern()
                

        if event.GetId() == ID_SYNC_CHOICE:
            print 'Choice: ' + event.GetString()
            self.controller.setSync(event.GetString())
            #
            # Meme - probably want to check to see if the x0xb0x responded before
            # making the switch permanent.
            #
            self.controller.SetConfigValue('syncchoice', event.GetString())



    def HandleMenuAction(self, event):
        if event.GetId() == ID_FILE_ABOUT:
            self.AboutBox()

        elif event.GetId() == ID_FILE_EXIT:
            self.Close(true)

        elif event.GetId() == ID_X0XB0X_RECONNECT_SERIAL:
            print "reconnectiong"
            self.controller.closeSerialPort()
            self.controller.openSerialPort()

        elif event.GetId() == ID_X0XB0X_PING:
            self.controller.sendPing()
                        
            
        elif event.GetId() == ID_X0XB0X_UPLOAD_FIRMWARE:
            d = wxFileDialog(self, 'Choose a x0xb0x firmware file', style = wxOPEN, wildcard = "HEX files (*.hex)|*.hex|All files (*.*)|*.*")
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
            d = wxFileDialog(self, 'Save EEPROM image to...', style = wxSAVE, wildcard = "x0xb0x pattern files (*.xbp)|*.xbp|All files (*.*)|*.*")
            d.ShowModal()
            if len(d.GetPath()) != 0:
                self.controller.backupAllPatterns(d.GetPath())

        elif event.GetId() == ID_X0XB0X_RESTORE_EEPROM:
            #
            # Retore EEPROM
            #
            d = wxFileDialog(self, 'Choose a x0xb0x EEPROM image file', style = wxOPEN, wildcard = "x0xb0x pattern files (*.xbp)|*.xbp|All files (*.*)|*.*")
            d.ShowModal()
            if len(d.GetPath()) != 0:
                self.controller.restoreAllPatterns(d.GetPath())

        elif event.GetId() == ID_X0XB0X_ERASE_EEPROM:
            dlg = wxMessageDialog(self,
                                  message = 'You are about to erase all of the patterns on your x0xb0x.  Are you sure you want to proceed?',
                                  caption = "WARNING",
                                  style = (wxICON_EXCLAMATION | wxYES_NO | wxNO_DEFAULT))
            
            if dlg.ShowModal() == wxID_YES:
                self.controller.eraseAllPatterns()
            else:
                pass
            
        elif event.GetId() >= ID_SERIAL_PORT:
            self.controller.selectSerialPort(self.portMenu.GetLabel(event.GetId()))


    def HandleTextEnterEvent(self,event):

        if event.GetId() == ID_LENGTH_TEXT:
            try:
                val = int(self.lengthText.GetValue())
                print "New length: " + str(val)
                self.patternEditGrid.SetPatternLength(val)
                self.OnGridChange()
            except ValueError, e:
                # This exception fires if enter is pressed when the text
                # box is empty.  In this case, just ignore the keypress.
                pass
            

# -------------------------------------------------------
#
# VALIDATOR CLASS
#

class TextValidator(wx.PyValidator):
    def __init__(self, range=[]):
        wx.PyValidator.__init__(self)
        self.range = range
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return TextValidator(self.range)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        
        try:
            if not (ord(val) in self.range):
                return False
        except Exception, e:
            return False
        
        return True


    def OnChar(self, event):
        key = event.KeyCode()
        tc = self.GetWindow()
        val = tc.GetValue()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if (val + chr(key)) in self.range:
            event.Skip()
            return

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return
