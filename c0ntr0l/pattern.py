
from Globals import *

NOTE_MASK = 0x3F
SLIDE_MASK = 0x80
ACCENT_MASK = 0x40

C1 = 0x30
C2 = 0x80

class Pattern:

    def __init__(self):
        self.notes = []
        self.length = 0

    #
    # Init with a pattern
    #
    def __init__(self, pstring):

        self.notes = []
        self.length = len(pstring)
        
        for i in range( len(pstring) ):
            self.notes.append( Note(pstring[i]) )

    def note(self, note): 
        return self.notes[note]

    def toByteString(self):
        pstring = ''
        for i in range( len(self.notes) ):
            pstring = pstring + self.notes[i].toByte()


#
# Note object
#
class Note:

    def __init__(self, byteNote):

        if ord(byteNote) == 0:
            self.rest = True
            return None
        
        self.note = ord(byteNote) & 0x3F
        self.accent = not ((ord(byteNote) & ACCENT_MASK) == 0)
        self.slide = not((ord(byteNote) & SLIDE_MASK) == 0)
        self.rest = False

        rawNote = ord(byteNote) & NOTE_MASK
        if (rawNote > C2):
            self.transpose = TRANSPOSE_UP
            self.note = rawNote - C2
        elif (rawNote < C1):
            self.transpose = TRANSPOSE_DOWN
            self.note = rawNote + C1
        else:
            self.transpose = TRANSPOSE_NONE
            self.note = rawNote

    def toByte(self):
        
        if self.transpose == TRANSPOSE_UP:
            rawnote = chr(self.note + C2)
        elif self.transpose == TRANSPOSE_DOWN:
            rawnote = chr(self.note - C1)
        else:
            rawnote = chr(self.note)

        if self.accent:
            rawnote |= ACCENT_MASK

        if self.slide:
            rawnote |= SLIDE_MASK
