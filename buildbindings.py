#!/usr/bin/python
import os
import re
from cppentities import *


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
                # Get the tag name, its the name of the class.
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
                            class_.addDestructor(destructor)
                        except ValueError:
                            raise Exception("The given line does not appear to ba a valid C++ prototype line at all...")
                print("---------------------")
        print(class_)


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
    # TODO Add some error messages if ctags is not available on the current machine.
    os.system('ctags --extra=+q --exclude=*.cpp --exclude=*.c --languages=C++ -f ' + tagFilePath + ' *')


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
