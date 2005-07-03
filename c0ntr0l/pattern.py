from Globals import *

NOTE_MASK = 0x3F
SLIDE_MASK = 0x80
ACCENT_MASK = 0x40

C2 = 0x17
C3 = 0x23

REST_NOTE = 0x00
NULL_NOTE = 0xFF

class Pattern:

    def __init__(self):
        self.notes = []

    def appendNote(self, noteName, accent, slide, transpose):
        self.notes.append( Note(noteName, accent, slide, transpose) )
        
    #
    # Init with a pattern
    #
    def __init__(self, pstring):

        self.notes = []
        
        for i in range( len(pstring) ):
            if ord(pstring[i]) == NULL_NOTE:
                break
            else:
                note = Note()
                note.parseNoteByte( pstring[i] )
                self.notes.append( note )

    def note(self, note):
        if note < self.length:
            return self.notes[note]
        else:
            raise PatternException("Attempted to access a note number greater than current pattern size")

    def toByteString(self):
        pstring = ''
        for i in range( len(self.notes) ):
            pstring = pstring + self.notes[i].toByte()

    def length(self):
        return len(self.notes)


#
# Note object
#
# All notes are initialized as rests.
#
class Note:

    def __init__(self):
        self.setToRest()

    def setToRest(self):
        self.note = REST_NOTE
        self.accent = False
        self.slide = False
        self.transpose = TRANSPOSE_NONE

    def parseNoteByte(self, byteNote):

        self.accent = not ((ord(byteNote) & ACCENT_MASK) == 0)
        self.slide = not ((ord(byteNote) & SLIDE_MASK) == 0)
        rawNote = ord(byteNote) & NOTE_MASK

        if rawNote == REST_NOTE:
            self.setToRest()
            return self

        # Otherwise, this isn't a rest note:
        
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
            self.setToRest()
            return self

        self.note = noteMIDIDict[noteName]
        self.accent = accent
        self.slide = slide
        self.transpose = transpose

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



class PatternException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
