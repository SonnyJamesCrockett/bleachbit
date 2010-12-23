# vim: ts=4:sw=4:expandtab

## BleachBit
## Copyright (C) 2010 Andrew Ziem
## http://bleachbit.sourceforge.net
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.



"""
Check for updates via the Internet
"""


import gtk
import platform
import socket
import sys
import traceback
import urllib2
import xml.dom.minidom

import Common
from Common import _
from GuiBasic import open_url


def user_agent():
    """Return the user agent string"""
    __platform = platform.system() # Linux or Windows
    __os = platform.uname()[2] # e.g., 2.6.28-12-generic or XP
    if sys.platform == "win32":
        # misleading: Python 2.5.4 shows uname()[2] as Vista on Windows 7
        __os = platform.uname()[3][0:3] # 5.1 = Windows XP, 6.0 = Vista, 6.1 = 7
    elif sys.platform == 'linux2':
        dist = platform.dist() 
        # example: ('fedora', '11', 'Leonidas')
        # example: ('', '', '') for Arch Linux
        if 0 < len(dist[0]):
            __os = dist[0] + '/' + dist[1] + '-' + dist[2]
    elif sys.platform[:6] == 'netbsd':
        __sys = platform.system()
        mach = platform.machine()
        rel = platform.release()
        __os = __sys + '/' + mach+ ' '  + rel
    __locale = ""
    try:
        import locale
        __locale = locale.getdefaultlocale()[0] # e.g., en_US
    except:
        traceback.print_exc()

    agent = "BleachBit/%s (%s; %s; %s)" % (Common.APP_VERSION, \
        __platform, __os, __locale)
    return agent



def update_dialog(parent, updates):
    """Updates contains the version numbers and URLs"""
    dlg = gtk.Dialog(title = _("Update BleachBit"), \
        parent = parent, \
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
    dlg.set_default_size(250, 125)

    label = gtk.Label(_("A new version is available."))
    dlg.vbox.pack_start(label)

    for update in updates:
        ver = update[0]
        url = update[1]
        box_update = gtk.HBox()
        # TRANSLATORS: %s expands to version such as '0.8.4' or '0.8.5beta' or similar
        button_stable = gtk.Button(_("Update to version %s") % ver)
        button_stable.connect('clicked', lambda dummy: open_url(url, parent, False))
        button_stable.connect('clicked', lambda dummy: dlg.response(0))
        box_update.pack_start(button_stable, False, padding = 10)
        dlg.vbox.pack_start(box_update, False)

    dlg.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)

    dlg.show_all()
    dlg.run()
    dlg.destroy()

    return False



def check_updates():
    """Check for updates via the Internet"""
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', user_agent())]
    socket.setdefaulttimeout(Common.socket_timeout)
    handle = opener.open(Common.update_check_url)
    doc = handle.read()
    try:
        dom = xml.dom.minidom.parseString(doc)
    except:
        print doc
        raise
    def parse_updates(element):
        if element:
            ver = element[0].getAttribute('ver')
            url = element[0].firstChild.data
            return (ver, url)
        return ()

    updates = ((parse_updates(dom.getElementsByTagName("stable"),),
        (parse_updates(dom.getElementsByTagName("beta"),))))
    dom.unlink()

    return (updates)

