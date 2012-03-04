#!/usr/bin/python
import os
import subprocess
import re
from cppentities import *
from writers import *


class TagFile(object):
    """
    Object allowing to manipulate a tag file generated with exuberant ctags.
    """
    def __init__(self, tagFile):
        self._file = tagFile

    def generateClassNames(self, classes):
        """
        Retrieve all the classes defined in the tagfile.
        """
        print('Generating classes collection.')
        classRegex = re.compile(r'\tc$')
        for line in open(self._file):
            if classRegex.search(line):
                # Get the tag name, it's the name of the class.
                classes.append(line.strip().split()[0])

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
                # TODO FIXME stripping the regex matched group make CPPMethod constructor fail!
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
                            print destructor
                            class_.addDestructor(destructor)
                        except ValueError:
                            raise Exception("The given line does not appear to ba a valid C++ prototype line at all...")


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
    # FIXME why subprocess.check_call() does not work on ubuntu?
    cmd = 'ctags --extra=+q --exclude=*.cpp --exclude=*.c --languages=C++ -f ' + tagFilePath + ' *'
    os.system(cmd)
    # try:
        # subprocess.check_call(cmd)
    # except Exception:
    #     print('A problem occured during the generation of the tags.\n'
    #         'Exuberant Ctags is probably not available on your system.\n'
    #         'For Windows, you can find an installer here: http://ctags.sourceforge.net/\n'
    #         'For Linux systems, install the corresponding package.\n'
    #         'On Debian and Ubuntu it is called \'exuberant-ctags\'.')
    #     raise


if __name__ == '__main__':
    tagFilePath = 'pybindings.tags'
    generateTagsForCurrentDir(tagFilePath)

    tagFile = TagFile(tagFilePath)
    classNames = []
    tagFile.generateClassNames(classNames)
    print('Classes found in tags file:\n' + str(classNames))
    classes = []
    for className in classNames:
        newClass = CPPClass(className)
        tagFile.retrieveMethodsForClass(newClass)
        classes.append(newClass)

    # Filename of the C API file:
    apiFilename = 'pyndings'
    apiWriter = CAPIWriter(apiFilename + '.h')
    for class_ in classes:
        apiWriter.writeClass(class_)

    os.remove(tagFilePath)
