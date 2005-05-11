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
# Name:         Globals.py
# Purpose:      Global variables 
#
# Author:       Michael Broxton
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2004 by MIT Media Laboratory
#----------------------------------------------------------------------------

APP_NAME = "x0xb0x c0ontr0l"


NOTES_IN_PATTERN = 16


TRANSPOSE_UP = 1
TRANSPOSE_DOWN = -1
TRANSPOSE_NONE = 0

NOTE_REST = 0x00

# Serial port attributes.
DEFAULT_BAUD_RATE = 19200
DEFAULT_COMM_PORT = '/dev/cu.usbserial-3B1'
DEFAULT_TIMEOUT = 0.5



DATA_COLLECTION_TIMEOUT = 2
WAIT_TIME = range(10000)
TIME_DELAY_FOR_OSSEND = 1.5e-3   # Time delay between bytes when sending the OS
WINDOZE_TIME_DELAY_FOR_OSSEND = 0.8e-3
DEFAULT_SPOTLIGHT_SERIALPORT = 0
DEFAULT_DONGLE_SERIALPORT = 1


def hexToSignedInt(hexString) :
    hexString = hexString.upper()
    if int(hexString,16) > 0x7FFF :
        twosComp = ''
        hexString = str('%04X' % (int(hexString,16) - 1))
        for c in hexString :
            twosComp = twosComp + str('%01X' % abs(int(c,16) - 15))
        return -1*int(twosComp,16)
    return int(hexString,16)

def opj(path):
    """Convert paths to the platform-specific separator"""
    return apply(os.path.join, tuple(path.split('/')))

