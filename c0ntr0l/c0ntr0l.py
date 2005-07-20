#!/bin/env python

#
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
# Name:         main.py
# Purpose:      
#
# Author:       Michael Broxton
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2005
#----------------------------------------------------------------------------

## import all of the wxPython GUI package
from wxPython.wx import *

from Globals import *
import model
import controller
import view

#---------------------------------------------------------------------------
# Every wxWindows application must have a class derived from wxApp.  The wxApp
# class sets up the basic event handling system (which is behind the scenes --
# you never really see it, but you can access it through calls to the wxApp object).
# Once everything for the wxApp has been properly initialized, the OnInit() function
# is called, where your code takes over to spawn windows in the GUI and initialize app
# logic.
#
# This particular application is built around the
# Model-View-Controller abstraction for graphical user interfaces.
# This means that in addition to creating objects for the graphical
# user interface and the software itself, this class acts as a
# controller that is the intermediary -- the abstraction barrier --
# between software and the graphical interface.
#
# Thus, beyond the initialization routine ( OnInit() ) that gets everything
# going, this class will have two types of methods: 1) Methods that are called
# when events occur in the GUI that need to interact with software components
# in the back end (actions), and 2) Methods that are called by the software back end
# to update the state of the GUI (outlets).
#---------------------------------------------------------------------------
class x0xc0ntr0l_App(wxApp):

    #
    # =================== Initialization =========================
    # wxPython calls this method to initialize the application.
    # This is where the controller object creates the model and
    # view objects.
    #
    def OnInit(self):
        # Create the controller, then the model and the view.
        c = controller.Controller(self)

        # Create the data model.  this should take care of serial ports
        # and application logic.
        m = model.Model(c)

        # Create the View class and the GUI.
        v = view.View(c)

        c.setView(v)
        c.setModel(m)

        m.initialize()
        v.initialize()

        self.m = m
        self.c = c
        self.v = v

        # Return a success flag
        return true

    def OnExit(self):
        # Save the configuration to file and exit.

        self.v.destroy()
        self.m.destroy()
        self.c.destroy()


#---------------------------------------------------------------------------

x0x_app = x0xc0ntr0l_App(0)          # Create an instance of the application class
x0x_app.MainLoop()                   # Tell it to start processing events

#----------------------------------------------------------------------------
