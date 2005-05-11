from wxPython.wx import *
from Globals import *
import wx.grid as gridlib

NOTE_ROW = 0
GRAPHIC_ROW = 1
EFFECT_ROW = 2


NoteKeymapDict = {'A' : 'A',
                  'B' : 'B',
                  'C' : 'C',
                  'D' : 'D',
                  'E' : 'E',
                  'F' : 'F',
                  'G' : 'G',
                  'H' : 'C2'}

SharpKeymapDict = { 'A' : 'A#',
                    'C' : 'C#',
                    'D' : 'D#',
                    'F' : 'F#',
                    'G' : 'G#'}
                 
class PatternEditGrid(gridlib.Grid):
    
    def __init__(self, parent, position):
        gridlib.Grid.__init__(self, parent, -1, pos = position, size = (512, 84))

        #
        # Add the text labels to the top and sides of the grid.
        #
        self.columnLabels = []
        for i in range(0, NOTES_IN_PATTERN):
            self.columnLabels.append(wxStaticText(parent, -1,
                                                  str(i + 1),
                                                  (position[0] + 12 + (i)*507/16, position[1] - 19)))

        wxStaticText(parent, -1, "Notes:", (position[0] - 46, position[1] + 8))
        wxStaticText(parent, -1, "Lengths:", (position[0] - 59, position[1] + 34))
        wxStaticText(parent, -1, "Effects:", (position[0] - 50, position[1] + 60))

        #
        # Create a wxGrid GUI object and configure it to show the pattern
        # editor.
        #
        self.CreateGrid(3, NOTES_IN_PATTERN)
        self.SetColLabelSize(0)
        self.SetRowLabelSize(0)
        self.SetMargins(-100, -100)
        self.SetDefaultCellAlignment(wxALIGN_CENTER, wxALIGN_CENTER)
        self.EnableEditing(False)
        self.DisableDragGridSize()

        self.noteBitmap = wxBitmap('resources/sixteenth.gif', wxBITMAP_TYPE_GIF)
        self.length = NOTES_IN_PATTERN

        #
        # Size the columns appropriately and enable them.  This also
        # clears their contents.
        #
        for i in range(0,16):            
            self.SetColSize(i, 512/16)
            self.enableColumn(i)
        for i in range(0,3):
            self.SetRowSize(i, 84/3)
            
        #
        # Bind some event handlers to deal with keystroke
        # navigation around the grid.
        #    
        gridlib.EVT_GRID_CELL_LEFT_CLICK(self, self.OnGridClick)
        EVT_KEY_DOWN(self, self.OnKeyDown)


    # ---------- EVENT HANDLERS ----------------

    #
    # Event handler for keyboard actions
    # 
    def OnKeyDown(self, evt):
        handled = False
        #
        # When the enter key is pressed, we move to the right.
        # At the end of the line, we wrap from the top row to
        # the bottom row, and vice versa.  The middle row wraps
        # to itself.
        #
        if (evt.KeyCode() == WXK_RETURN or
            evt.KeyCode() == WXK_SPACE or
            evt.KeyCode() == WXK_TAB):
            
            self.MoveRightWithSpecialWrap()
            handled = True
            
        elif evt.KeyCode() == WXK_BACK:
            self.MoveLeftWithSpecialWrap()
            handled = True

        #
        # We override right and left keyboard events so that we
        # can wrap around the grid when you push up against either
        # side.
        #
        elif evt.KeyCode() == WXK_RIGHT:
            self.MoveRightWithWrap()
            handled = True

        elif evt.KeyCode() == WXK_LEFT:
            self.MoveLeftWithWrap()
            handled = True

        elif ((evt.KeyCode() == ord('r')) or (evt.KeyCode() == ord('R'))) and (self.GetGridCursorCol() < self.length):
            self.SetNoteToRest(self.GetGridCursorCol())
            self.MoveRightWithWrap()
            handled = True
            
        #
        # Handle key presses for changing the notes in the pattern
        #
        if (self.GetGridCursorRow() == NOTE_ROW or
            self.GetGridCursorRow() == GRAPHIC_ROW):

            if (not evt.ShiftDown()):
                # Process lowercase keystrokes, which produce natural notes
                for keyChar in NoteKeymapDict.keys():
                    if evt.KeyCode() == ord(keyChar) and (self.GetGridCursorCol() < self.length):
                        self.SetCellValue(NOTE_ROW,
                                          self.GetGridCursorCol(),
                                          NoteKeymapDict[keyChar])
                        self.SetCellValue(GRAPHIC_ROW, self.GetGridCursorCol(), '1')
                        self.MoveRightWithWrap()
                        handled = True
            else:
                # Process Capital keystrokes, which create notes with sharps
                for keyChar in SharpKeymapDict.keys():
                    if evt.KeyCode() == ord(keyChar) and (self.GetGridCursorCol() < self.length):
                        self.SetCellValue(NOTE_ROW,
                                          self.GetGridCursorCol(),
                                          SharpKeymapDict[keyChar])
                        self.SetCellValue(GRAPHIC_ROW, self.GetGridCursorCol(), '1')        
                        self.MoveRightWithWrap()
                        handled = True
                        
        #
        # Handle key presses for changing the effects
        #
#        if (self.GetGridCursorRow() == EFFECT_ROW):
#            for keyChar in NoteKeymapDict.keys():
#                if evt.KeyCode() == ord(keyChar):
#                    print 'Got the effect ' + NoteKeymapDict[keyChar] + '!'
#                    handled = True
            
            
        #
        # If all other cases fall through, we must pass
        # the event up to the default event handler for the
        # wx.Grid.
        #
        if not handled:
            evt.Skip()

    #
    # Event handler for mouse clicks
    #   
    def OnGridClick(self, evt):
        if (evt.GetRow() == GRAPHIC_ROW) and (evt.GetCol() < self.length):
            self.SetNoteToRest(evt.GetCol())

        #
        # Make sure we are not clicking on an inactive square.  There
        # should be no way to select an inactive square.
        #
        if (evt.GetCol() < self.length):
            self.SetFocus()
            evt.Skip()



    # ---------- PATTERN EDIT GRID UTILITIES ----------------

    #
    # Set a note in the pattern to a rest.  The note is specified
    # using a zero-based integer index in the range [0, 15]
    #
    def SetNoteToRest(self, note):
        self.SetCellValue(NOTE_ROW, note, ' ')
        self.SetCellValue(GRAPHIC_ROW, note, '0')
        self.SetCellValue(EFFECT_ROW, note, ' ')


    def SetPatternLength(self, newLength):
        for i in range(self.length,newLength):
            self.enableColumn(i)
        for i in range(newLength, NOTES_IN_PATTERN):
            self.disableColumn(i)            
        self.length = newLength

        #
        # Finally, we have to check to make sure that the grid
        # cursor isn't outside of the valid region.  If it is,
        # reset its position to (0,0)
        #
        if self.GetGridCursorCol() >= newLength:
            self.SetGridCursor(0,0)


    def enableColumn(self, col):
        self.SetCellValue(NOTE_ROW, col, ' ')
        self.SetCellValue(GRAPHIC_ROW, col, '0')
        self.SetCellRenderer(GRAPHIC_ROW, col, NoteRenderer(self.noteBitmap))
        self.SetCellValue(EFFECT_ROW, col, ' ')

        for i in range(0,3):
            self.SetCellBackgroundColour(i, col, wxWHITE)

        self.columnLabels[col].Show(True)

    def disableColumn(self, col):
        self.SetCellValue(NOTE_ROW, col, ' ')
        self.SetCellValue(GRAPHIC_ROW, col, ' ')
        self.SetCellRenderer(GRAPHIC_ROW, col, None)
        self.SetCellValue(EFFECT_ROW, col, ' ')

        for i in range(0,3):
            self.SetCellBackgroundColour(i, col, wxLIGHT_GREY)

        self.columnLabels[col].Show(False)



    def MoveRightWithWrap(self):
        if self.GetGridCursorCol() + 1 == self.length:
            self.SetGridCursor(self.GetGridCursorRow(), 0)
        else:
            self.MoveCursorRight(False)

    def MoveLeftWithWrap(self):
        if self.GetGridCursorCol() == 0:
            self.SetGridCursor(self.GetGridCursorRow(), self.length - 1)
        else:
            self.MoveCursorLeft(False)

    #
    # The "special" wrap moves the cursor from the note row down to the effect
    # and from the effect row back up to the note row.  This makes entering patterns
    # slightly faster and easier, since it saves the pattern writer the time that
    # would be consumed moving the cursor to the bottom row themselves.
    #
    def MoveRightWithSpecialWrap(self):
        if self.GetGridCursorCol() + 1 == self.length:
            if self.GetGridCursorRow() == NOTE_ROW:
                self.SetGridCursor(EFFECT_ROW, 0)
            elif self.GetGridCursorRow() == GRAPHIC_ROW:
                self.SetGridCursor(GRAPHIC_ROW, 0)
            elif self.GetGridCursorRow() == EFFECT_ROW:
                self.SetGridCursor(NOTE_ROW, 0)
        else:
            self.MoveCursorRight(False)

    def MoveLeftWithSpecialWrap(self):
        if self.GetGridCursorCol() == 0:
            if self.GetGridCursorRow() == NOTE_ROW:
                self.SetGridCursor(EFFECT_ROW, self.length - 1)
            elif self.GetGridCursorRow() == GRAPHIC_ROW:
                self.SetGridCursor(GRAPHIC_ROW, self.length - 1)
            elif self.GetGridCursorRow() == EFFECT_ROW:
                self.SetGridCursor(NOTE_ROW, self.length - 1)
        else:
            self.MoveCursorLeft(False)


    # ------------ CONVERSION METHODS -------------------
    #
    # The following methods convert the data in the grid
    # to and from a pattern object which can be passed to
    # or provided by the data model.
    #
    # ---------------------------------------------------

    def update(self,pattern):
        for i in range(0, pattern.length):
            
            if pattern.note(i).rest:
                self.SetCellValue(0, i, '')
                self.SetCellValue(1, i, '')
                self.SetCellValue(2, i, '')

            else:    
                self.SetCellValue(0, i, chr(pattern.note(i).note))
                self.SetCellValue(1, i, 'O')
                
                efx = ''
                if pattern.note(i).accent:
                    efx += 'A'
                elif pattern.note(i).slide:
                    efx += 'S'
                elif pattern.note(i).transpose == TRANSPOSE_UP:
                    efx += 'U'
                elif pattern.note(i).transpose == TRANSPOSE_DOWN:
                    efx += 'D'
                self.SetCellValue(2, i, efx)

    def pattern(self):
        pass



# ----------------------------------------------------------------
class NoteRenderer(gridlib.PyGridCellRenderer):
    def __init__(self, noteBitmap):
        gridlib.PyGridCellRenderer.__init__(self)
        self.noteBitmap = noteBitmap

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        dc.SetBackgroundMode(wxSOLID)
        dc.SetBrush(wxBrush(wxWHITE, wxSOLID))
        dc.SetPen(wxTRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        if grid.GetCellValue(row,col) != str(0):
            dc.DrawBitmap(self.noteBitmap, rect.x, rect.y, True)

    def GetBestSize(self, grid, attr, dc, row, col):
        w = self.noteBitmap.GetWidth()
        h = self.noteBitmap.GetHeight()
        return wxSize(w, h)

    def Clone(self):
        return NoteRenderer(self.noteBitmap)
