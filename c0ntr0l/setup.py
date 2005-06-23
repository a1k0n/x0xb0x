#!/usr/bin/env python
"""
setup.py - script for building the c0ntr0l application into
a bundle (MacOS X) or exe (windows).

A distutils script to make a standalone .exe of superdoodle for
Windows platforms.  You can get py2exe from
http://py2exe.sourceforge.net/.  Use this command to build the .exe
and collect the other needed files:

Windows Usage:
    python setup.py py2exe


Also a distutils script to make a standalone .app of superdoodle for
Mac OS X.  You can get py2app from http://undefined.org/python/py2app.
Use this command to build the .app and collect the other needed files:

Mac Usage:
    % python setup.py py2app

"""
from distutils.core import setup
import sys

if sys.platform == 'darwin':
    import py2app
    buildstyle = 'app'
elif sys.platform == 'win32':
    import py2exe
    # buildstyle = 'console'
    buildstyle = 'windows'


#
# Here are some py2app options that effect the build process for
# MacOS X.  You can see a full list of options by running
# the command
#
#    % python setup.py py2app -h
#
# Note that you must replace hypens '-' with underscores '_'
# when converting option names from the command line to a script.
# For example, the --argv-emulation option is passed as 
# argv_emulation in an options dict.
py2app_options = dict(
    # Map "open document" events to sys.argv.
    # Scripts that expect files as command line arguments
    # can be trivially used as "droplets" using this option.
    # Without this option, sys.argv should not be used at all
    # as it will contain only Mac OS X specific stuff.
    argv_emulation=True,

    # This is a shortcut that will place MyApplication.icns
    # in the Contents/Resources folder of the application bundle,
    # and make sure the CFBundleIcon plist key is set appropriately.
    iconfile='resources/c0ntr0l.icns',

    # Include the following 3rd party packages in the bundle.
    packages='serial,wx,wxPython',
)


#
# Here are some py2app options that effect the build process for
# Windows.  You can see a full list of options by running
# the command
#
#    % python setup.py py2exe -h
#
py2exe_options = dict(
    # Include the following 3rd party packages in the bundle.
    packages='serial,wx,wxPython',
)

# The wxpython code often depends on certain resource files
# (sounds, images, etc.).  These must be explicitly included
# in the bundle using the command below.

wx_datafiles = ['./resources']



# Finally, we are ready to specify the arguments to the distutils
# setup command.

setup(
    app = ['c0ntr0l.py'],
    data_files = wx_datafiles,
    options = dict(
        # Each command is allowed to have its own
        # options, so we must specify that these
        # options are py2app specific.
        py2app = py2app_options,
        py2exe = py2exe_options
    )
)
