from wxPython.wx import *
from Globals import *
import wx.grid as gridlib

NOTE_ROW = 0
GRAPHIC_ROW = 1
EFFECT_ROW = 2

NOTES_IN_PATTERN = 16

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
    
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, pos = (70, 130), size = (512, 84))

        self.CreateGrid(3, 16)
        self.SetColLabelSize(0)
        self.SetRowLabelSize(0)
        self.SetMargins(-100, -100)
        self.DisableDragGridSize()
        self.SetDefaultCellAlignment(wxALIGN_CENTER, wxALIGN_CENTER)

        noteBitmap = wxBitmap('resources/sixteenth.gif', wxBITMAP_TYPE_GIF)
        
        for i in range(0,16):            
            self.SetColSize(i, 512/16)
            self.SetCellRenderer(1, i, NoteRenderer(noteBitmap))
        for i in range(0,3):
            self.SetRowSize(i, 84/3)
            
        self.EnableEditing(False)
        self.DisableDragGridSize()

        gridlib.EVT_GRID_CELL_LEFT_CLICK(self, self.OnGridClick)
        EVT_KEY_DOWN(self, self.OnKeyDown)
        #
        # Why doesn't this line work instead?
        #
        # self.Bind(wxEVT_KEY_DOWN, self.OnKeyDown)


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
        if evt.KeyCode() == WXK_RETURN:
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

        elif (evt.KeyCode() == ord('r')) or (evt.KeyCode() == ord('R')):
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
                    if evt.KeyCode() == ord(keyChar):
                        self.SetCellValue(NOTE_ROW,
                                          self.GetGridCursorCol(),
                                          NoteKeymapDict[keyChar])
                        self.SetCellValue(GRAPHIC_ROW, self.GetGridCursorCol(), '1')
                        self.MoveRightWithWrap()
                        handled = True
            else:
                # Process Capital keystrokes, which create notes with sharps
                for keyChar in SharpKeymapDict.keys():
                    if evt.KeyCode() == ord(keyChar):
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
        
    def OnGridClick(self, evt):
        if evt.GetRow() == GRAPHIC_ROW:
            self.SetNoteToRest(evt.GetCol())
        self.SetFocus()
        evt.Skip()

    #
    # Set a note in the pattern to a rest.  The note is specified
    # using a zero-based integer index in the range [0, 15]
    #
    def SetNoteToRest(self, note):
        self.SetCellValue(NOTE_ROW, note, ' ')
        self.SetCellValue(GRAPHIC_ROW, note, '0')
        self.SetCellValue(EFFECT_ROW, note, ' ')


    def MoveRightWithWrap(self):
        success = self.MoveCursorRight(False)
        if not success:
            self.SetGridCursor(self.GetGridCursorRow(), 0)

    def MoveLeftWithWrap(self):
        success = self.MoveCursorLeft(False)
        if not success:
            self.SetGridCursor(self.GetGridCursorRow(), NOTES_IN_PATTERN - 1)


    #
    # The "special" wrap moves the cursor from the note row down to the effect
    # and from the effect row back up to the note row.  This makes entering patterns
    # slightly faster and easier, since it saves the pattern writer the time that
    # would be consumed moving the cursor to the bottom row themselves.
    #
    def MoveRightWithSpecialWrap(self):
        success = self.MoveCursorRight(False)
        if not success:
            if self.GetGridCursorRow() == NOTE_ROW:
                self.SetGridCursor(EFFECT_ROW, 0)
            elif self.GetGridCursorRow() == GRAPHIC_ROW:
                self.SetGridCursor(GRAPHIC_ROW, 0)
            elif self.GetGridCursorRow() == EFFECT_ROW:
                self.SetGridCursor(NOTE_ROW, 0)

    def MoveLeftWithSpecialWrap(self):
        success = self.MoveCursorLeft(False)
        if not success:
            if self.GetGridCursorRow() == NOTE_ROW:
                self.SetGridCursor(EFFECT_ROW, 15)
            elif self.GetGridCursorRow() == GRAPHIC_ROW:
                self.SetGridCursor(GRAPHIC_ROW, 15)
            elif self.GetGridCursorRow() == EFFECT_ROW:
                self.SetGridCursor(NOTE_ROW, 15)

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
