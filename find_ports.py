#!/usr/bin/env python
#
# Serial port enumeration. Console tool and backend selection.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# # # Modified to return ports as list # # #
#
# SPDX-License-Identifier:    BSD-3-Clause

"""
This module will provide a function called run that returns an
iterable (generator or list) that will enumerate available com ports. Note that
on some systems non-existent ports may be listed.

Additionally a grep function is supplied that can be used to search for ports
based on their descriptions or hardware ID.
"""

from __future__ import absolute_import

import sys
import os
import re
import numpy as np

# chose an implementation, depending on os
#~ if sys.platform == 'cli':
#~ else:
if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
#~ elif os.name == 'java':
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def grep(regexp, include_links=False):
    """
    Search for ports using a regular expression. Port name, description and
    hardware ID are searched. The function returns an iterable that returns the
    same tuples as comport() would do.
    """
    r = re.compile(regexp, re.I)
    for info in comports(include_links):
        port, desc, hwid = info
        if r.search(port) or r.search(desc) or r.search(hwid):
            yield info


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def run():
 
    hits = 0
    iterator = sorted(comports(include_links=False))
    # list them
    ports = ["","","","",""]
    for n, (port, desc, hwid) in enumerate(iterator, 1):
        #sys.stdout.write("{:20}\n".format(port))
        ports[n] = port
        sys.stdout.write("    desc: {}\n".format(desc))
        sys.stdout.write("    hwid: {}\n".format(hwid))
        hits += 1
    portlist = []
    y = 0
    for n, l in enumerate(ports):
        x = 0
        if x < hits:
            if ports[n] != "":
                portlist.append(ports[n])
                x += 1
    return portlist, hits
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
