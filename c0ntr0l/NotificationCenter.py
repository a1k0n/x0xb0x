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
# Name:         NotificationCenter.py
# Purpose:      The abstract class of a notification center.  A notification
#               center is an abstract class that can become the parent
#               of any normal class. It enables an instance of the
#               child class to notifify a number of other objects,
#               dubbed listeners, of events that occur within the
#               class.  An example of a notification center might be a
#               serial port object that notifies various other object
#               instances when each new byte of data is received over
#               the serial port.  
#
#               Notification centers and listeners can be chained
#               together (a listener can itself be a notification
#               center) in "notification trees" which propagate new
#               data throughout a hierarchy of objects as it becomes
#               available.
#
#               When a listener registers with a notification center,
#               it must specify an 'key' to specify what data it is
#               interested in being notified about.  This key must
#               match the key that is provided when the
#               NotifyListeners() routine is called by the
#               notification center.  The key is usually specific to
#               the type of data being provided by the class.  For
#               example, if the data being passed to listeners is a
#               communication packet, a natural key might be packet
#               type, packet source, or packet destination.  If a
#               listener registers with the wildcard key 'ALL' (the
#               python string), it will receive notifications whenever
#               any data is published by the Notification Center,
#               regardless of its key.
#
# author:       Michael Broxton and Josh Lifton
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2004 by MIT Media Laboratory
#----------------------------------------------------------------------------

class NotificationCenter:
    def __init__(self):
        #
        # Create an empty list
        #
        self._listeners = []  

    #
    # Register the object 'listener' with this notification center for the
    # notification 'key'.
    #
    def RegisterListener(self, listener, key):
        newTuple = (listener, key)
        if newTuple not in self._listeners:
            self._listeners.append(newTuple)

    #
    # Unregister the object 'listener' with this notification center for the
    # notification 'key'.
    #
    def UnregisterListener(self, listener, key):
        newTuple = (listener, key)
        if newTuple in self._listeners:
            self._listeners.remove(newTuple)


    #
    # Notify all currently registered listeners that new data is
    # available.  Each listener is checked to see if this listener is
    # concerned with this particular piece of data.  This check is
    # accomplished using the data key.  A data key of 'ALL' will
    # ensure that the listener receives all data notifications.
    #
    def NotifyListeners(self, data, publisherKey):
        for x in self._listeners:
            if (x[1] == 'ALL') or (x[1] == publisherKey):
                (x[0]).NotificationCallback(data)
