#!/usr/bin/python
# Copyright 2012 Florent Galland
# 
# This file is part of pybindings.
# 
# pybindings is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pybindings is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pybindings.  If not, see <http://www.gnu.org/licenses/>.
import os
# import subprocess
import re
from cppentities import CPPClass, CPPConstructor, CPPDestructor, CPPMethod
from writers import PyAPIWriter


class TagFile(object):
    """
    Object allowing to manipulate a tag file generated with exuberant ctags.
    """
    def __init__(self, tagFile):
        self._file = tagFile

    def generateClassNamesAndFiles(self, classesAndFiles):
        """
        Retrieve all the classes defined in the tagfile and the *.h file they come from.

        The parameter 'classes' is a list of tuples (className, classHeaderFileName)
        """
        print('Generating classes collection.')
        classRegex = re.compile(r'\tc$')
        for line in open(self._file):
            if classRegex.search(line):
                # The first word is the tag name, it's the name of the class.
                # The second word is the header file it comes from.
                classesAndFiles.append((line.strip().split()[0], line.strip().split()[1]))

    def retrieveMethodsForClass(self, class_):
        """
        Retrieve all the methods prototypes corresponding
        to the given class name.
        """
        print('Retrieving methods for class ' + class_.getName() + '.')
        methodRegex = re.compile(r'^\s*~?\w+\s+.*\tf\tclass:' + class_.getName() + '$')
        prototypeRegex = re.compile(r'\/\^(.+)\$\/;\"')
        for line in open(self._file):
            if methodRegex.search(line):
                # print(line)
                # Get the prototype of the method, constructor or destructor
                # contained in the line.
                # FIXME stripping the regex matched group make 
                # the CPPMethod constructor fail!
                prototype = prototypeRegex.search(line).group(1)
                print(prototype)
                try:
                    method = CPPMethod(prototype)
                    class_.addMethod(method)
                except ValueError:
                    try:
                        constructor = CPPConstructor(prototype)
                        class_.addConstructor(constructor)
                    except ValueError:
                        try:
                            destructor = CPPDestructor(prototype)
                            class_.addDestructor(destructor)
                        except ValueError:
                            raise Exception('The given line does not appear to'
                            'be a valid C++ prototype line at all...')


def parseHeader(headerPath):
    print('Parsing header: ' + headerPath)
    classRegex = re.compile(r'^\s*\b(class)\b')
    with open(headerPath) as h:
        for line in h:
            if classRegex.match(line):
                print(line)
                print(classRegex.match(line).groups())


def generateTagsForCurrentDir(tagFilePath):
    """
    Generate a tag file for all the C++ headers in the current directory.
    """
    print('Generating tags...')
    # FIXME why subprocess.check_call() does not work on Ubuntu but
    # it works on Debian?
    cmd = 'ctags --extra=+q --exclude=*.cpp --exclude=*.c --languages=C++ -f ' + tagFilePath + ' *'
    os.system(cmd)
    # try:
        # subprocess.check_call(cmd)
    # except Exception:
        # print('A problem occured during the generation of the tags.\n'
            # 'Exuberant Ctags is probably not available on your system.\n'
            # 'For Windows, you can find an installer here: http://ctags.sourceforge.net/\n'
            # 'For Linux systems, install the corresponding package.\n'
            # 'On Debian and Ubuntu it is called \'exuberant-ctags\'.')
        # raise

def main():
    tagFilePath = 'pybindings.tags'
    generateTagsForCurrentDir(tagFilePath)

    tagFile = TagFile(tagFilePath)
    classesAndFiles = []
    tagFile.generateClassNamesAndFiles(classesAndFiles)
    print('Classes found in tags file:')
    for classAndFile in classesAndFiles:
        print('    ' + classAndFile[0] + ' from file ' + classAndFile[1])
    classes = []
    includes = []
    for classAndFile in classesAndFiles:
        newClass = CPPClass(classAndFile[0])
        tagFile.retrieveMethodsForClass(newClass)
        classes.append(newClass)
        includes.append(classAndFile[1])

    # Write the C API file:
    apiFilename = 'pyndings'
    library = 'libpyndings.so'
    apiWriter = PyAPIWriter(apiFilename, includes, library)
    apiWriter.writeClasses(classes)

    # Remove temporary files.
    os.remove(tagFilePath)


if __name__ == '__main__':
    main()

