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
                # Get the tag name, its the name of the class.
                classes.append(line.strip().split()[0])

    def retrieveMethodsForClass(self, className, methods):
        """
        Retrieve all the methods prototypes corresponding
        to the given class name.
        """
        print('Retrieving methods for class ' + className + '.')
        methodRegex = re.compile(r'\tf\tclass:' + className + '$')
        for line in open(self._file):
            if methodRegex.search(line):
                print(line)
                # Get the prototype of the method, constructor or destructor
                # contained in the line.
                classEntity = None
                try:
                    method = CPPMethod(line.strip())
                except ValueError:
                    try:
                        method = CPPConstructor(line.strip())
                    except ValueError:
                        try:
                            method = CPPDestructor(line.strip())
                        except ValueError:
                            raise Exception("The given line does not appear to ba a valid C++ prototype line at all...")
                print("---------------------")
                #methods.append(line.strip().split()[0])


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
    print('Classes found in tags file:\n' + str(classes))
    for currentClass in classes:
        methods = []
        tagFile.retrieveMethodsForClass(currentClass, methods)
