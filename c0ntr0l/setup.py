#!/usr/bin/env python

from distutils.core import setup
import py2exe

setup(name='c0ntr0l',
      version='1.0',
      description='x0xb0x interface software',
      author='the br0x & Limor Fried',
      url='http://www.ladyada.net/make/x0xb0x',
      options = {'py2exe': {'excludes': ['javax.comm', 'FCNTL', 'TERMIOS']}},
      py_modules=['c0ntr0l'],
      windows=["c0ntr0l.py"]
     )
