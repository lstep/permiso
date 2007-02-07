# -*- coding: utf-8 -*-
"""
Copyright (C) 2007 Adelux <contact@adelux.fr>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import optparse,os,sys,glob
from pkg_resources import Requirement, resource_filename, resource_string, resource_stream, resource_listdir

sys.path.insert(0, os.getcwd())

#from permiso import collector

def main():
    #parser = optparse.OptionParser(usage="%prog", version=expediar.__version__)
    #parser.add_option('-a', '--action', help="Action", dest="action")

    #(options, args) = parser.parse_args()

    #if not os.geteuid()==0:
    #    sys.exit("\nOnly root can run this function\n")

    #os.system('/usr/bin/twistd --no_save --syslog -noy /usr/bin/expediar.tac')
    #os.system('/usr/bin/twistd --no_save -noy /usr/bin/expediar.tac')

    import sys, os, string

    if string.find(os.path.abspath(sys.argv[0]), os.sep+'Twisted') != -1:
        sys.path.insert(0, os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir)))
    if hasattr(os, "getuid") and os.getuid() != 0:
        sys.path.insert(0, os.path.abspath(os.getcwd()))

    from twisted.scripts.twistd import run
    sys.argv.extend(['-y', resource_filename('expediar','data/bin/collector.tac')])
    sys.argv.extend(['--pidfile', '/var/tmp/collector.pid'])
    run()

