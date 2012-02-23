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
        for line in open(self._file):
            if methodRegex.search(line):
                print(line)
                # Get the prototype of the method, constructor or destructor
                # contained in the line.
                method = None
                try:
                    method = CPPMethod(line.strip())
                except ValueError, e:
                    print(e)
                    try:
                        method = CPPConstructor(line.strip())
                    except ValueError, e:
                        print(e)
                        try:
                            method = CPPDestructor(line.strip())
                        except ValueError, e:
                            print(e)
                            raise Exception("The given line does not appear to ba a valid C++ prototype line at all...")
                print(method.getContainedString()
                #methods.append(line.strip().split()[0])



class CPPEntityBase(object):
    """CPPEntityBase is the base class for all objects representing C++ stuff."""
    def getContainedString():
        raise NotImplementedError

    @staticmethod
    def getPattern():
        raise NotImplementedError


class CPPValue(CPPEntityBase):
    """
    CPPValue represents a C++ value type,
    that is, a type and its attributes (const and/or pointer or reference).
    """
    def __init__(self, valueString):
        pass

    @staticmethod
    def getPattern():
        return r'(const)?\s+(\w+)(::)?(\w+)?\s*(&\|*)?'


class CPPMethod(CPPEntityBase):
    """
    CPPMethod represents a C++ method generic prototype.
    For the moment, template methods are not handled.
    A C++ method is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field has the tag '?'
    So:
    [const]? [namespace]? [return value] [reference or pointer]? [method name] [parameter 1]? [const]?
    """
    def __init__(self, prototypeString):
        if re.search(CPPMethod.getPattern(), prototypeString):
            print(re.search(CPPMethod.getPattern(), prototypeString).groups())
        else:
            raise ValueError("The given prototypeString is not a valid C++ method prototype.")

    @staticmethod
    def getPattern():
        return r'\/\^\s*' + CPPValue.getPattern() + r'\s+(\w+)'


class CPPConstructor(CPPEntityBase):
    """
    CPPConstructor represents a C++ method generic constructor.
    A C++ constructor is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field has the tag '?'
    So:
    [class name] [parameter 1]?
    """
    def __init__(self, prototypeString):
        if re.search(CPPConstructor.getMethodPattern(), prototypeString):
            print(re.search(CPPConstructor.getMethodPattern(), prototypeString).groups())
        else:
            raise ValueError("The given prototypeString is not a valid C++ constructor prototype.")

    @staticmethod
    def getPattern(className):
        return r'\/\^\s*' + className + r'\(\)'


class CPPDestructor(CPPEntityBase):
    """
    CPPDestructor represents a C++ method generic destructor.
    A C++ destructor is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field has the tag '?'
    So:
    ~[class name]()
    """
    def __init__(self, prototypeString):
        if re.search(CPPDestructor.getPattern(), prototypeString):
            print(re.search(CPPDestructor.getPattern(), prototypeString).groups())
        else:
            raise ValueError("The given prototypeString is not a valid C++ destructor prototype.")

    @staticmethod
    def getPattern(className):
        return r'\/\^\s*~' + className + r'\(\)'


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
        tagFile.retrieveMethodsForClass(currentClass, methods)
