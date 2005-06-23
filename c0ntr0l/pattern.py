
from Globals import *

NOTE_MASK = 0x3F
SLIDE_MASK = 0x80
ACCENT_MASK = 0x40


C2 = 0x17
C3 = 0x23

class Pattern:

    def __init__(self):
        self.notes = []
        self.length = 0

    def appendNote(self, noteName, accent, slide, transpose):
        self.notes.append( Note(noteName, accent, slide, transpose) )
        
    #
    # Init with a pattern
    #
    def __init__(self, pstring):

        self.notes = []
        self.length = len(pstring)
        
        for i in range( len(pstring) ):
            note = Note()
            note.parseNoteByte( pstring[i] )
            self.notes.append( note )

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

    def __init__(self):
        self.rest = True

    def parseNoteByte(self, byteNote):

        if ord(byteNote) == 0:
            self.rest = True
            return self
        
        self.accent = not ((ord(byteNote) & ACCENT_MASK) == 0)
        self.slide = not ((ord(byteNote) & SLIDE_MASK) == 0)
        self.rest = False

        rawNote = ord(byteNote) & NOTE_MASK
        if (rawNote > C3):
            self.transpose = TRANSPOSE_UP
            rawNote = rawNote - 12
        elif (rawNote < C2):
            self.transpose = TRANSPOSE_DOWN
            rawNote = rawNote + 12
        else:
            self.transpose = TRANSPOSE_NONE

        self.note = rawNote

    def parseNoteArgs(self, noteName, accent, slide, transpose):
        if noteName == '':
            self.rest = True
            return self

        self.note = noteMIDIDict[noteName]
        self.accent = accent
        self.slide = slide
        self.transpose = transpose
        self.rest = False

    def toByte(self):        
        if self.transpose == TRANSPOSE_UP:
            rawnote = self.note + 12
        elif self.transpose == TRANSPOSE_DOWN:
            rawnote = self.note - 12
        else:
            rawnote = self.note

        if self.accent:
            rawnote |= ACCENT_MASK

        if self.slide:
            rawnote |= SLIDE_MASK

        return chr(rawnote)
