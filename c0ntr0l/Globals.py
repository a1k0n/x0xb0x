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
# Purpose:      Global variables for the Pushpin Debugger
#
# Author:       Michael Broxton and Josh Lifton
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2004 by MIT Media Laboratory
#----------------------------------------------------------------------------

#Super Important Information!!!
CLOCK_TICKS_PER_METER = 5317.0

# Information about packets.
PACKET_HEADER_SIZE = 8
PACKET_HEADER_SIZE_WITHOUT_CRCS = 6
IDE_REQUEST_MESSAGE = '77'
IDE_DUMP_MESSAGE_SIZE = 62
OS_HEADER_MESSAGE = 'BB'
TOF_ELECT_MESSAGE = '55'
TOF_ANCHOR_MESSAGE = '56'
IDE_DUMP_MESSAGE = '99'
SYN_TEST_MESSAGE = 'AA'
IR_FRAME_START_BYTE = '50'
REQUEST = IR_FRAME_START_BYTE
END_REQUEST = '5A'
DONT_WAIT_FOR_OS = 'CC'
WAIT_FOR_OS = 'CD'
ROUTED_REQUEST_MESSAGE = '78'
ROUTED_REPLY_MESSAGE = '79'
BEGIN_DATA_HARVEST = '7A'
SET_COLOR_MESSAGE = '3A'
SET_LED_STATE_MESSAGE = '3B'
REBOOT_MESSAGE = '3C'
SENT_MESSAGE = '3D'

# Addresses all Pushpins know about.
GLOBALADDRESS = '00'
IDEADDRESS = 'FF'

# Packet types.
SYN='00'
BROADCAST='01'
ACK='02'
NAK='03'

# Serial port attributes.
DEFAULT_BAUD_RATE = 19200
DEFAULT_COMM_PORT = 0
DEFAULT_TIMEOUT = 0.5
DATA_COLLECTION_TIMEOUT = 2
WAIT_TIME = range(10000)
TIME_DELAY_FOR_OSSEND = 1.5e-3   # Time delay between bytes when sending the OS
WINDOZE_TIME_DELAY_FOR_OSSEND = 0.8e-3
DEFAULT_SPOTLIGHT_SERIALPORT = 0
DEFAULT_DONGLE_SERIALPORT = 1

SPOTLIGHT = 0
DONGLE = 1

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
