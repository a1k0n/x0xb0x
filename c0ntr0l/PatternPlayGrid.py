from wxPython.wx import *
from Globals import *
import wx.grid as gridlib

PATTERNS_PER_BANK = 8
                 
class PatternPlayGrid(gridlib.Grid):
    
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, pos = (70, 340), size = (512, 64))


        self.CreateGrid(1, PATTERNS_PER_BANK)
        self.SetColLabelSize(0)
        self.SetRowLabelSize(0)
        self.SetMargins(-100, -100)

        self.EnableEditing(False)
        self.DisableDragGridSize()

        for i in range(0,8):            
            self.SetColSize(i, 512/8)
            self.SetRowSize(0, 64)


        gridlib.EVT_GRID_CELL_LEFT_CLICK(self, self.OnGridClick)
        EVT_KEY_DOWN(self, self.OnKeyDown)

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
        if evt.KeyCode() == WXK_RIGHT:
            self.MoveRightWithWrap()
            handled = True
            
        elif (evt.KeyCode() == WXK_BACK) or (evt.KeyCode() == WXK_LEFT):
            self.MoveLeftWithWrap()
            handled = True

        elif (evt.KeyCode() == WXK_RETURN) or (evt.KeyCode() == ord(' ')):
            #
            # Set the current pattern
            #
            handled = True

        #
        # If all other cases fall through, we must pass
        # the event up to the default event handler for the
        # wx.Grid.
        #
        if not handled:
            evt.Skip()
        
    def OnGridClick(self, evt):
        #
        # Set the current pattern to the grid square that was clicked on...
        #
        print "Grid click on column: " + str(evt.GetCol())
        self.SetFocus()
        evt.Skip()

    def MoveRightWithWrap(self):
        success = self.MoveCursorRight(False)
        if not success:
            self.SetGridCursor(0, 0)

    def MoveLeftWithWrap(self):
        success = self.MoveCursorLeft(False)
        if not success:
            self.SetGridCursor(0, PATTERNS_PER_BANK - 1)

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
