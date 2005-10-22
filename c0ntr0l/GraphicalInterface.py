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
# Author:       Michael Broxton & Limor Fried
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2005 by MIT Media Laboratory
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


DEFAULT_MAINWINDOW_SIZE = (600, 450)
DEFAULT_MAINWINDOW_POS = (150, 150)     # Default position

LABEL_TO_OBJ_PAD = 5

#
# Widget ID definitions for the event handling system.
#
ID_MAIN_WINDOW = wxNewId()

ID_FILE_EXIT = wxNewId() 
ID_FILE_ABOUT = wxNewId()

ID_EDIT_CUT = wxNewId()
ID_EDIT_COPY = wxNewId()
ID_EDIT_PASTE = wxNewId()
ID_EDIT_SHIFTR = wxNewId()
ID_EDIT_SHIFTL = wxNewId()

ID_X0XB0X_UPLOAD_FIRMWARE = wxNewId()
ID_X0XB0X_DUMP_EEPROM = wxNewId()
ID_X0XB0X_RESTORE_EEPROM = wxNewId()
ID_X0XB0X_ERASE_EEPROM = wxNewId()
ID_X0XB0X_CONNECT = wxNewId()
ID_X0XB0X_DISCONNECT = wxNewId()
ID_X0XB0X_RECONNECT_SERIAL = wxNewId()
ID_X0XB0X_REFRESH_SERIAL = wxNewId()
ID_X0XB0X_PING = wxNewId()

ID_PORTMENU = wxNewId()

ID_SERIAL_PORT = 10000


ID_PE_LOC_TEXT = wxNewId()
ID_PE_BANK_TEXT = wxNewId()
ID_LENGTH_TEXT = wxNewId()
ID_TEMPO_TEXT = wxNewId()
ID_TEMPO_SLIDER = wxNewId()
ID_RUNSTOP_BUTTON = wxNewId()
ID_SAVE_PATTERN_BUTTON = wxNewId()
ID_PLAY_PATTERN_BUTTON = wxNewId()
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
                         style=(wxDEFAULT_FRAME_STYLE ^ wxRESIZE_BORDER) |wxNO_FULL_REPAINT_ON_RESIZE)

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

        # create a clipboard/buffer to hold copied patterns
        self.pattern_clipboard = 0

        # Disable things at the beginning
        self.x0xb0xDisable()
        
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
        logo.SetPosition((DEFAULT_MAINWINDOW_SIZE[0] - logo.GetSize()[0] - 20, 20))

        biglabelfont = wxFont(14, wxTELETYPE, wxNORMAL, wxNORMAL, faceName = "Courier")

        

        #
        # ==== Pattern Edit Section ====
        #

        divider1 = wxStaticLine(self, -1, pos = (15,55), size = (569,1), style = wxLI_HORIZONTAL)

        
        label1 = wxStaticText(self, -1, "Pattern Edit", (20, 64))
        label1.SetFont(biglabelfont)

        #
        # Pattern Edit Grid
        #
        loc = (label1.GetPosition()[0] +  50,
               label1.GetPosition()[1] + label1.GetSize()[1] + 20)
        self.patternEditGrid = PatternEditGrid(self, loc)

        
        labelfont = wxFont(11, wxDEFAULT, wxNORMAL, wxNORMAL)
        smallfont = wxFont(8, wxDEFAULT, wxNORMAL, wxNORMAL)

        # Bank select control       
        bankStrings = []
        for i in range(1, NUMBER_OF_BANKS + 1):
            bankStrings.append(str(i))
        self.pe_bankText = wxChoice(self, ID_PE_BANK_TEXT,
                                    (71,
                                     self.patternEditGrid.GetPosition()[1] +
                                     self.patternEditGrid.GetSize()[1] + 15),
                                    (0,0),
                                    choices = bankStrings)
        self.pe_bankText.SetFont(smallfont)
        self.pe_bankText.SetSize((60, self.pe_bankText.GetBestSize()[1] - 3))

        self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.pe_bankText)

        pe_label1 = wxStaticText(self, -1, "Bank:", (36, 228),
                                 style = wxALIGN_RIGHT)
        pe_label1.SetFont(labelfont)
        pe_label1.SetSize(pe_label1.GetBestSize())
        pe_label1.SetPosition((self.pe_bankText.GetPosition()[0] -
                               LABEL_TO_OBJ_PAD -
                               pe_label1.GetSize()[0],
                               self.pe_bankText.GetPosition()[1] + 3));
        
        # Location Select Control

        pe_label2 = wxStaticText(self, -1, "Loc:", (18, 253), style = wxALIGN_RIGHT)
        pe_label2.SetFont(labelfont)
        pe_label2.SetSize(pe_label2.GetBestSize())
        pe_label2.SetPosition((self.pe_bankText.GetPosition()[0] + self.pe_bankText.GetSize()[0] + 15,
                               pe_label1.GetPosition()[1]));
        
        locStrings = []
        for i in range(1, LOCATIONS_PER_BANK + 1):
            locStrings.append(str(i))
        self.pe_locText = wxChoice(self, ID_PE_LOC_TEXT, 
                                   (pe_label2.GetPosition()[0] + pe_label2.GetSize()[0] + 5,
                                    self.pe_bankText.GetPosition()[1]),
                                   (0,0),
                                   choices = locStrings)
        self.pe_locText.SetFont(smallfont)
        self.pe_locText.SetSize((60, self.pe_locText.GetBestSize()[1] - 3))
        self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.pe_locText)

        # Pattern length control
        pattlenStrings = []
        for i in range(0, NOTES_IN_PATTERN + 1):
            pattlenStrings.append(str(i))
        self.lengthText = wxChoice(self, ID_LENGTH_TEXT,
                                   (self.patternEditGrid.GetPosition()[0]+
                                    self.patternEditGrid.GetSize()[0] - 40,
                                    self.pe_bankText.GetPosition()[1]),
                                   (39,19),
                                   choices = pattlenStrings)
        self.lengthText.SetFont(smallfont)
        self.lengthText.SetSize(self.lengthText.GetBestSize())
        self.lengthText.Disable()
        
        self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.lengthText)

        pe_label2 = wxStaticText(self, -1, "Pattern Length:",
                                 (450, self.pe_bankText.GetPosition()[1]),
                                 style = wxALIGN_RIGHT)
        pe_label2.SetFont(labelfont)
        pe_label2.SetSize(pe_label2.GetBestSize())

        pe_label2.SetPosition((self.lengthText.GetPosition()[0] -
                              pe_label2.GetSize()[0] - 5,
                               self.pe_bankText.GetPosition()[1] + 3));

#        EVT_TEXT(self.lengthText, self.HandleKeyAction)
#        EVT_KEY_DOWN(self.lengthText, self.HandleKeyAction)

        # Play button
        self.pe_PlayButton = wxButton(self, ID_PLAY_PATTERN_BUTTON,
                                      "Play Pattern",
                                      (self.patternEditGrid.GetPosition()[0],
                                       self.lengthText.GetPosition()[1] +
                                       self.lengthText.GetSize()[1] + 15),
                                      (0, 0))
        self.pe_PlayButton.SetFont(smallfont)
        self.pe_PlayButton.SetSize((100, self.pe_PlayButton.GetBestSize()[1] - 5))
        self.pe_PlayButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, self.pe_PlayButton)

        # Save button
        self.pe_SaveButton = wxButton(self, ID_SAVE_PATTERN_BUTTON,
                                      "Save Pattern",
                                      (self.patternEditGrid.GetPosition()[0]+
                                       self.patternEditGrid.GetSize()[0] - 100,
                                       self.lengthText.GetPosition()[1] +
                                       self.lengthText.GetSize()[1] + 15),
                                      (0, 0))
        self.pe_SaveButton.SetFont(smallfont)
        self.pe_SaveButton.SetSize((100, self.pe_SaveButton.GetBestSize()[1] - 5))
        
        self.pe_SaveButton.Disable()
        self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, self.pe_SaveButton)


        
        #
        # ==== Pattern Play Section ====
        #
        #divider2 = wxStaticLine(self, -1,
        #                        pos = (15, self.pe_SaveButton.GetPosition()[1] +
        #                               self.pe_SaveButton.GetSize()[1] + 15),
        #                        size = (569,1), style = wxLI_HORIZONTAL)
        #label2 = wxStaticText(self, -1, "Pattern Play",
        #                      (divider2.GetPosition()[0]+5,
        #                       divider2.GetPosition()[1]+5))
        #label2.SetFont(biglabelfont)

        #self.patternPlayGrid = PatternPlayGrid(self)

        # Man, couldnt you put this in the widget -- ada
        #for i in range(1,9):
        #    wxStaticText(self, -1, str(i), (96 + (i-1)*515/8, 318))
        #wxStaticText(self, -1, "Pattern:", (17, 362))
        

        #
        # Other controls and buttons in the Pattern Play section
        #
        #pp_button1 = wxButton(self, ID_RUNSTOP_BUTTON, "R/S");
        #pp_button1.SetFont(smallfont)
        #pp_button1.SetPosition((self.patternPlayGrid.GetPosition()[0] + 3,
        #                        self.patternPlayGrid.GetPosition()[1] +
        #                        self.patternPlayGrid.GetSize()[1] + 5))
        #pp_button1.SetSize((pp_button1.GetBestSize()[0],
        #                    pp_button1.GetBestSize()[1]- 5))
        #pp_button2 = wxButton(self, ID_PP_LOAD_BANK_BUTTON, "Load", (518, 413), (66, 17))
        #self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, pp_button1)
        #self.Bind(wx.EVT_BUTTON, self.HandleButtonAction, pp_button2)
        
        #pp_label1 = wxStaticText(self, -1, "Bank:", (436, 415), style = wxALIGN_RIGHT)
        #pp_label1.SetFont(labelfont)
        #pp_label1.SetSize(pp_label1.GetBestSize())

        #textValidator = TextValidator(map(str, range(1, NUMBER_OF_BANKS + 1))) 
        #self.pp_bankSelect = wxTextCtrl(self, -1, "1", (476,412), (39,19),
        #                                style = (wxTE_PROCESS_ENTER),
        #                                validator = textValidator)

        divider3 = wxStaticLine(self, -1, pos = (15,self.pe_SaveButton.GetPosition()[1]+50), size = (569,1),
                                style = wxLI_HORIZONTAL)
        label3 = wxStaticText(self, -1, "Global Parameters",
                              (divider3.GetPosition()[0]+5, divider3.GetPosition()[1]+10))
        label3.SetFont(biglabelfont)
        
        # 
        # The tempo and sync source controls appear in the very bottom of the
        # window.
        #
        tempoLabel = wxStaticText(self, -1, "Tempo:",
                                 (label3.GetPosition()[0]+10,
                                  label3.GetPosition()[1]+label3.GetSize()[1]+15),
                                 style = wxALIGN_LEFT)
        tempoLabel.SetFont(labelfont)
        tempoLabel.SetSize(tempoLabel.GetBestSize())

#        textValidator = TextValidator(map(str, range(1, NOTES_IN_PATTERN + 1)))        
        self.tempoText = wxTextCtrl(self, ID_TEMPO_TEXT, '0',
                                    (tempoLabel.GetPosition()[0]+tempoLabel.GetSize()[0]+5,
                                     tempoLabel.GetPosition()[1]), (39,19),
                                     style = (wxTE_PROCESS_ENTER))
        #self.Bind(wx.EVT_TEXT_ENTER, self.HandleTextEnterEvent)

        self.tempoSlider = wxSlider(self, id=ID_TEMPO_SLIDER, minValue = 20, maxValue=300,
                                    pos=(self.tempoText.GetPosition()[0] + 50,
                                         self.tempoText.GetPosition()[1]),
                                    name="Tempo")
        self.tempoSlider.SetSize((400,
                                  self.tempoSlider.GetBestSize()[1]));
        self.Bind(wx.EVT_SLIDER, self.HandleSlider, self.tempoSlider)
        

        #syncText = wxStaticText(self, -1, "Select sync mode:", (350, 486), style = wxALIGN_LEFT)
        #syncText.SetFont(labelfont)
        #syncText.SetSize(syncText.GetBestSize())
        
        #syncList = [SYNCMSG_OUT, SYNCMSG_IN_MIDI, SYNCMSG_IN_DIN]
        #self.syncChoice = wxChoice(self, ID_SYNC_CHOICE, (454, 484), choices = syncList)
        #self.Bind(wx.EVT_CHOICE, self.HandleChoiceAction, self.syncChoice)
        #self.syncChoice.SetSelection(0)

        #try:
        #    syncPreference = self.controller.GetConfigValue('syncchoice')
        #    for i in range(0,len(syncList)):
        #        if syncPreference == syncList[i]:
        #            self.syncChoice.SetSelection(i)
        #except ConfigException, e:
        #    # No preference yet exists for sync source.
        #    pass

        #self.controller.setSync(self.syncChoice.GetString(self.syncChoice.GetSelection()))

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
        
        self.aboutmenu = wxMenu()
        self.aboutmenu.Append(ID_FILE_ABOUT, "About", "About This Program")
        self.aboutmenu.Append(ID_FILE_EXIT, "Quit\tCTRL-Q", "Exit the Program")
        menubar.Append(self.aboutmenu, "File")

        self.editmenu = wxMenu()
        #self.editmenu.Append(ID_EDIT_CUT, "Cut Pattern\tCTRL_X", "Cut pattern from EEPROM")
        self.editmenu.Append(ID_EDIT_COPY, "Copy Pattern\tCTRL-C", "Copy pattern from EEPROM")
        self.editmenu.Append(ID_EDIT_PASTE, "Paste Pattern\tCTRL-V", "Paste pattern to EEPROM")
        self.editmenu.AppendSeparator()
        self.editmenu.Append(ID_EDIT_SHIFTR, "Shift Right\tSHIFT-ARROW-RIGHT", "Shift pattern one step to the right")
        self.editmenu.Append(ID_EDIT_SHIFTL, "Shift Left\tSHIFT-ARROW-LEFT", "Shift pattern one step to the left")
        menubar.Append(self.editmenu, "Edit")
        
        self.x0xmenu = wxMenu()
        self.x0xmenu.Append(ID_X0XB0X_UPLOAD_FIRMWARE, "Upload firmware...\tCTRL-U", "Upload a new .HEX file to the x0xb0x firmware")
        self.x0xmenu.AppendSeparator()
        self.x0xmenu.Append(ID_X0XB0X_DUMP_EEPROM, "Backup EEPROM", "Backup EEPROM to the hard disk")
        self.x0xmenu.Append(ID_X0XB0X_RESTORE_EEPROM, "Restore EEPROM", "Restore EEPROM from a backup on the hard drive")
        self.x0xmenu.AppendSeparator()
        self.x0xmenu.Append(ID_X0XB0X_ERASE_EEPROM, "Erase EEPROM", "Erase the patterns on your x0xb0x.")
        menubar.Append(self.x0xmenu, "x0xb0x")

        self.serialmenu = wxMenu()
        self.portMenu = wx.Menu()
        self.serialmenu.Append(ID_X0XB0X_RECONNECT_SERIAL, "Reconnect serial port\tCTRL-R")
        self.serialmenu.Append(ID_X0XB0X_PING, "Send serial ping\tCTRL-P")
        self.serialmenu.AppendSeparator()
        #menu.AppendMenu(ID_X0XB0X_REFRESH_SERIAL, "Refresh serial port list")
        self.serialmenu.AppendMenu(ID_PORTMENU, 'Port', self.portMenu)
        menubar.Append(self.serialmenu, 'Serial')
        
            
        self.SetMenuBar(menubar)


        #
        # Create event bindings for each of the menu options specified above.
        # 
        EVT_MENU(self, ID_FILE_ABOUT, self.HandleMenuAction)
        EVT_MENU(self, ID_FILE_EXIT, self.HandleMenuAction)

        #EVT_MENU(self, ID_EDIT_CUT, self.HandleMenuAction)
        EVT_MENU(self, ID_EDIT_COPY, self.HandleMenuAction)
        EVT_MENU(self, ID_EDIT_PASTE, self.HandleMenuAction)
        EVT_MENU(self, ID_EDIT_SHIFTR, self.HandleMenuAction)
        EVT_MENU(self, ID_EDIT_SHIFTL, self.HandleMenuAction)

        EVT_MENU(self, ID_X0XB0X_CONNECT, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_DISCONNECT, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_RECONNECT_SERIAL, self.HandleMenuAction)
        EVT_MENU(self, ID_X0XB0X_REFRESH_SERIAL, self.HandleMenuAction)
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
        aboutString = ('(c) 2005 Michael Broxton & Limor Fried.\n\n' +
                       'For more information about the x0xb0x, check out http://www.ladyada.net/make/x0xb0x\n')
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
                self.lengthText.Disable()
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

# quickies

    def x0xb0xEnable(self):
        # enable stuff!
        self.x0xmenu.Enable(ID_X0XB0X_DUMP_EEPROM, True)
        self.x0xmenu.Enable(ID_X0XB0X_RESTORE_EEPROM, True)
        self.x0xmenu.Enable(ID_X0XB0X_ERASE_EEPROM, True)
        self.serialmenu.Enable(ID_X0XB0X_RECONNECT_SERIAL, True)
        self.serialmenu.Enable(ID_X0XB0X_PING, True)
        self.serialmenu.Enable(ID_PORTMENU, False)
        self.x0xmenu.Enable(ID_X0XB0X_UPLOAD_FIRMWARE, False)
        if (self.serialmenu.FindItemById(ID_X0XB0X_CONNECT) != None):
            self.serialmenu.Remove(ID_X0XB0X_CONNECT)
        self.serialmenu.Insert(0, ID_X0XB0X_DISCONNECT, "Disconnect x0xb0x")
        self.pe_bankText.Enable();
        self.pe_locText.Enable();
        self.editmenu.Enable(ID_EDIT_COPY, True)
        self.editmenu.Enable(ID_EDIT_PASTE, True)
        self.editmenu.Enable(ID_EDIT_SHIFTR, True)
        self.editmenu.Enable(ID_EDIT_SHIFTL, True)
        self.tempoSlider.Enable()
        
    def x0xb0xDisable(self):
        self.x0xmenu.Enable(ID_X0XB0X_DUMP_EEPROM, False)
        self.x0xmenu.Enable(ID_X0XB0X_RESTORE_EEPROM, False)
        self.x0xmenu.Enable(ID_X0XB0X_ERASE_EEPROM, False)
        self.serialmenu.Enable(ID_X0XB0X_RECONNECT_SERIAL, False)
        self.serialmenu.Enable(ID_X0XB0X_PING, False)
        self.serialmenu.Enable(ID_PORTMENU, True)
        self.x0xmenu.Enable(ID_X0XB0X_UPLOAD_FIRMWARE, True)
        if (self.serialmenu.FindItemById(ID_X0XB0X_DISCONNECT) != None):
            self.serialmenu.Remove(ID_X0XB0X_DISCONNECT)
        self.serialmenu.Insert(0, ID_X0XB0X_CONNECT, "Connect to x0xb0x")
        self.pe_bankText.Disable();
        self.pe_locText.Disable();
        self.editmenu.Enable(ID_EDIT_COPY, False)
        self.editmenu.Enable(ID_EDIT_PASTE, False)
        self.editmenu.Enable(ID_EDIT_SHIFTR, False)
        self.editmenu.Enable(ID_EDIT_SHIFTL, False)
        self.tempoSlider.Disable()
    #
    # ====================== Actions ============================
    #

    def HandleButtonAction(self,event):
        if event.GetId() == ID_SAVE_PATTERN_BUTTON:
            if self.SavePattern():
                self.pe_SaveButton.Disable()
        elif event.GetId() == ID_PLAY_PATTERN_BUTTON:
            self.controller.playPattern
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
                
        if event.GetId() == ID_LENGTH_TEXT:
            val = int(self.lengthText.GetSelection())
            print "New length: " + str(val)
            self.patternEditGrid.SetPatternLength(val)
            self.OnGridChange()
                
        if event.GetId() == ID_SYNC_CHOICE:
            print 'Choice: ' + event.GetString()
            self.controller.setSync(event.GetString())
            #
            # Meme - probably want to check to see if the x0xb0x responded before
            # making the switch permanent.
            #
            self.controller.SetConfigValue('syncchoice', event.GetString())


    def HandleSlider(self, event):
        if (event.GetId() == ID_TEMPO_SLIDER):
            #print 'slid '+str(self.tempoSlider.GetValue())
            self.tempoText.SetValue(str(self.tempoSlider.GetValue()))
            self.controller.setTempo(self.tempoSlider.GetValue())

    def HandleMenuAction(self, event):
        if event.GetId() == ID_FILE_ABOUT:
            self.AboutBox()

        elif event.GetId() == ID_FILE_EXIT:
            self.Close(true)

        # Edit menu
        elif event.GetId() == ID_EDIT_COPY:
            self.pattern_clipboard = self.patternEditGrid.getPattern()
        elif event.GetId() == ID_EDIT_CUT:
            self.pattern_clipboard = self.patternEditGrid.getPattern()
            self.pe_SaveButton.Enable()
        elif event.GetId() == ID_EDIT_PASTE:
            if (self.pattern_clipboard != 0):
                self.patternEditGrid.update(self.pattern_clipboard)
                self.pe_SaveButton.Enable()
            else:
                print("nothing in clipboard!\n")

        elif event.GetId() == ID_EDIT_SHIFTR:
            tmp = self.patternEditGrid.getPattern()
            tmp.shift(-1)
            self.patternEditGrid.update(tmp)
            self.pe_SaveButton.Enable()
        elif event.GetId() == ID_EDIT_SHIFTL:
            tmp = self.patternEditGrid.getPattern()
            tmp.shift(1)
            self.patternEditGrid.update(tmp)
            self.pe_SaveButton.Enable()

        elif event.GetId() == ID_X0XB0X_CONNECT:
            print "Connecting..."
            if self.controller.openSerialPort():
                if self.controller.sendPing():
                    self.controller.connectSerialPort()
                    self.statusBar.SetStatusText("Found x0xb0x", 0)
                    self.controller.readTempo()
                    self.x0xb0xEnable()
                else:
                    self.controller.closeSerialPort()
                    self.statusBar.SetStatusText("Did not find x0xb0x", 0)


        elif event.GetId() == ID_X0XB0X_DISCONNECT:
            print "Disconnecting..."
            self.controller.closeSerialPort()
            self.statusBar.SetStatusText("Disconnected", 0)
            self.x0xb0xDisable()
            
        elif event.GetId() == ID_X0XB0X_RECONNECT_SERIAL:
            print "Reconnecting"
            self.controller.closeSerialPort()
            self.controller.openSerialPort()

        elif event.GetId() == ID_X0XB0X_PING:
            self.controller.sendPing()
                        
            
        elif event.GetId() == ID_X0XB0X_UPLOAD_FIRMWARE:
            d = wxFileDialog(self, 'Choose a x0xb0x firmware file', style = wxOPEN, wildcard = "HEX files (*.hex)|*.hex|All files (*.*)|*.*")
            d.ShowModal()
            if len(d.GetPath()) != 0:
                try:
                    self.controller.openSerialPort()
                    self.controller.uploadHexfile(d.GetPath())
                    self.controller.closeSerialPort()
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
            # Restore EEPROM
            #
            d = wxFileDialog(self, 'Choose a x0xb0x EEPROM image file', style = wxOPEN, wildcard = "x0xb0x pattern files (*.xbp)|*.xbp|All files (*.*)|*.*")
            d.ShowModal()
            if len(d.GetPath()) != 0:
                self.controller.restoreAllPatterns(d.GetPath())
            # the current pattern may have changed, reeeeload it!
            self.LoadPattern()

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
