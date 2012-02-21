#!/usr/bin/python
import os
import re


class TagFile(object):
    """
    Object allowing to manipulate a tag file generated with exuberant ctags.
    """
    def __init__(self, tagFile):
        self._file = tagFile

    def generateClassesCollection(self, classes):
        """
        Retrieve all the classes defined in the tagfile.
        """
        print('Generating classes collection.')
        classRegex = re.compile(r'\tc$')
        for line in open(self._file):
            if classRegex.search(line):
                print(line)
                # Get the tag name, its the name of the class.
                classes.append(line.strip().split()[0])

    def retrieveMethodsForClass(self, className, methods):
        """
        Retrieve all the methods prototypes corresponding
        to the given class name.
        """
        print('Retrieving methods for class ' + className + '.')
        methodRegex = re.compile(r'\tf\tclass:' + className + '$')
        #prototypeRegex = re.compile(r'/^\s*)
        #  \/\^\s*(const)?\s+(\w+)(::)?(\w+)?(&\|*)?\s+(\w+)
        for line in open(self._file):
            if methodRegex.search(line):
                print(line)
                # Get the prototype of the method.
                methods.append(line.strip().split()[0])


class CPPMethod(object):
    """
    CPPMethod represents a C++ method generic prototype.
    For the moment, template methods are not handled.
    A C++ method is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field as the tag '?'
    So:
    [const]? [namespace]? [return value] [reference or pointer]? [method name] [parameter 1]? [const]?
    """
    def __init__(self):
        pass


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
    os.system('ctags --extra=+q --exclude=*.cpp --exclude=*.c --languages=C++ -f ' + tagFilePath + ' *')


if __name__ == '__main__':
    #pdb.set_trace()
    tagFilePath = 'pybindings.tags'
    generateTagsForCurrentDir(tagFilePath)

    tagFile = TagFile(tagFilePath)
    classes = []
    tagFile.generateClassesCollection(classes)
    print(classes)
    for currentClass in classes:
        methods = []
        tagFile.retrieveMethodsForClass(currentClass)
