# vim: ts=4:sw=4:expandtab

## BleachBit
## Copyright (C) 2011 Andrew Ziem
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
Import Winapp2.ini (and Winapp1.ini) files
"""



import Cleaner
import Common
import ConfigParser
import os
import re
import sys

from Action import ActionProvider, Delete
from Common import _
from FileUtilities import listdir
from General import boolstr_to_bool, getText
from xml.dom.minidom import parseString


def xml_escape(s):
    """Lightweight way to escape XML entities"""
    return s.replace('&', '&amp;')


class Winapp:
    """Create cleaners from a Winapp2.ini-style file"""

    def __init__(self, pathname):
        """Create cleaners from a Winapp2.ini-style file"""

        self.cleaner = Cleaner.Cleaner()
        self.parser = ConfigParser.RawConfigParser()
        self.parser.read(pathname)
        self.cleaner.description = 'Winapp2.ini'
        for section in self.parser.sections():
            self.handle_section(section)


    def handle_section(self, section):
        """Parse a section"""
        self.cleaner.add_option(section, 'name', 'description')
        for option in self.parser.options(section):
            if option.startswith('filekey'):
                self.handle_filekey(section, option)
            elif option.startswith('regkey'):
                print 'fixme: regkey'
            elif option in ('default'):
                pass
            elif option in ('langsecref', 'detect'):
                print 'fixme:', option
            else:
                print 'WARNING: unknown option', option


    def __make_file_provider(self, dirname, filename, recurse, removeself):
        """Change parsed FileKey to action provider"""
        regex = ''
        if recurse:
            search = 'walk.files'
            path = dirname
            if filename.startswith('*.'):
                filename = filename.replace('*.', '.')
            if '.*' == filename:
                if removeself:
                    search = 'walk.all'
            else:
                regex = ' regex="%s" ' % (re.escape(filename) + '$')
        else:
            search = 'glob'
            path = os.path.join(dirname, filename)
            if -1 == path.find('*'):
                search = 'file'
        action_str = '<option command="delete" search="%s" path="%s" %s/>' % \
            (search, xml_escape(path), regex)
        print 'debug:', action_str
        yield Delete(parseString(action_str).childNodes[0])
        if removeself:
            action_str = '<option command="delete" search="file" path="%s"/>' % xml_escape(dirname)
            print 'debug:', action_str
            yield Delete(parseString(action_str).childNodes[0])


    def handle_filekey(self, section, option):
        """Parse a FileKey# option"""
        elements = self.parser.get(section, option).split('|')
        dirname = elements.pop(0)
        filename = ""
        if elements:
            filename = elements.pop(0)
        recurse = False
        removeself = False
        for element in elements:
            if 'RECURSE' == element:
                recurse = True
            elif 'REMOVESELF' == element:
                recurse = True
                removeself = True
            else:
                print 'WARNING: unknown file option', element
        print self.parser.get(section, option)
        for provider in self.__make_file_provider(dirname, filename, recurse, removeself):
            self.cleaner.add_action(section, provider)


    def get_cleaner(self):
        """Return the created cleaner"""
        return self.cleaner





