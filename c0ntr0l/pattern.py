from Globals import *

NOTE_MASK = 0x3F
SLIDE_MASK = 0x80
ACCENT_MASK = 0x40

C2 = 0x17
C3 = 0x23

REST_NOTE = 0x00
NULL_NOTE = 0xFF

class Pattern:

    def appendNote(self, noteNum, accent, slide, transpose):
        note = Note()
        note.parseNoteArgs(noteNum, accent, slide, transpose)
        self.notes.append(note)

    def shift(self, shiftamt):
        while (shiftamt != 0):
            if (shiftamt > 0):
                tempnote = self.notes[0]
                for i in range( 0, self.length() - 1 ):
                    self.notes[i] = self.notes[i+1]
                self.notes[self.length()-1] = tempnote
                shiftamt-=1
            if (shiftamt < 0):
                tempnote = self.notes[self.length() - 1]
                for i in range(1, self.length() ):
                    self.notes[self.length()-i] = self.notes[self.length()-1-i]
                self.notes[0] = tempnote
                shiftamt+=1


        
    #
    # Init with a pattern
    #
    def __init__(self, pstring = ''):

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
        for i in range( NOTES_IN_PATTERN ):
            if i < len(self.notes):
                pstring = pstring + self.notes[i].toByte()
            else:
                pstring = pstring + chr(NULL_NOTE)
        return pstring

    def length(self):
        return len(self.notes)


    def printMe(self):
        print '---> Pattern '
        for i in range(len(self.notes)):
            patstr = str(self.notes[i].note)
            efxstr = '        '
            if self.notes[i].accent:
                efxstr += 'A '
            if self.notes[i].slide:
                efxstr += 'S '
            if self.notes[i].transpose == TRANSPOSE_UP:
                efxstr += 'U '
            if self.notes[i].transpose == TRANSPOSE_DOWN:
                efxstr += 'D '
            print patstr + efxstr
        print '---->'
        

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

    def parseNoteArgs(self, noteNum, accent, slide, transpose):
        if (noteNum < BOTTOM_NOTE) or (noteNum > TOP_NOTE) or (noteNum == REST_NOTE):
            self.setToRest()
            return self

        self.note = noteNum
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
