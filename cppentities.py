#!/usr/bin/python
import re
import unittest


class CPPClass(object):
    """A whole C++ class with all its potential constructors, methods and destructor."""
    def __init__(self, className):
        # Set default values.
        self._name = className
        self._constructors = []
        self._destructor = None
        self._methods = []

    def getName(self):
        return self._name

    def addConstructor(self, constructor):
        self._constructors.append(constructor)

    def addDestructor(self, destructor):
        self._destructor = destructor

    def addMethod(self, method):
        self._methods.append(method)

    def __str__(self):
        string = ''
        for constructor in self._constructors:
            string += str(constructor) + '\n'
        string += str(self._destructor) + '\n'
        for method in self._methods:
            string += str(method) + '\n'
        return string


class CPPValue(object):
    """
    CPPValue represents a C++ value type,
    that is, a type and its attributes (const and/or pointer or reference).
    """
    def __init__(self, valueString):
        if re.search(CPPValue.getPattern(), valueString):
            self._match = re.search(CPPValue.getPattern(), valueString)

            # Set default values.
            self._const = False
            self._namespace = None
            self._type = None
            self._reference = False
            self._pointer = False

            self._const = self._match.group(1)
            if self._match.group(3):
                self._namespace = self._match.group(2)
                self._type = self._match.group(4)
                self._reference = (self._match.group(5) == '&')
                self._pointer = (self._match.group(5) == '*')
            else:
                self._namespace = None
                self._type = self._match.group(2)
                self._reference = (self._match.group(3) == '&')
                self._pointer = (self._match.group(3) == '*')
        else:
            raise ValueError("The given prototypeString is not a valid C++ value.")

    def getMatchedGroups(self):
        return self._match.groups()

    def isConst(self):
        return self._const

    def getNamespace(self):
        return self._namespace

    def getType(self):
        return self._type

    def isReference(self):
        return self._reference

    def isPointer(self):
        return self._pointer

    def __str__(self):
        return (str(self.isConst()) + ' ' + str(self.getNamespace()) + ' ' +
        str(self.getType()) + ' ' + str(self.isReference() or self.isPointer()))

    @staticmethod
    def getPattern():
        return r'\s*(const)?\s*(\w+)(::)?(\w+)?\s*(\&\|\*)?'

    @staticmethod
    def getPatternWithoutGroups():
        return r'\s*(?:const)?\s*\w+(?:::)?(?:\w+)?\s*(?:\&\|\*)?'


class CPPMethod(object):
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
            self._match = re.search(CPPMethod.getPattern(), prototypeString)
            print(self._match.groups())

            # Set default values.
            self._returnValue = None
            self._name = ''

            # The first group is a CPPValue so build it.
            self._returnValue = CPPValue(self._match.group(1))
            self._name = self._match.group(2)
            self._parameters = self._match.group(3)
        else:
            raise ValueError("The given prototypeString is not a valid C++ method prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def getReturnValue(self):
        return self._returnValue

    def getName(self):
        return self._name

    def __str__(self):
        return str(self.getReturnValue()) + ' ' + self.getName()

    # @staticmethod
    # def getPattern():
    #     return (r'\s*(' +
    #         CPPValue.getPatternWithoutGroups() +
    #         r')\s+(\w+)')

    # @staticmethod
    # def getPattern():
    #     return (r'\s*(' +
    #         CPPValue.getPatternWithoutGroups() +
    #         r')\s+(\w+)\s*\(\s*(' +
    #         CPPValue.getPatternWithoutGroups() +
    #         r')?\s+(\w+)?\s*\)')

    @staticmethod
    def getPattern():
        return (r'\s*(' +
            CPPValue.getPatternWithoutGroups() +
            r')\s+(\w+)')


class CPPConstructor(object):
    """
    CPPConstructor represents a C++ method generic constructor.
    A C++ constructor is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field has the tag '?'
    So:
    [class name] [parameter 1]?
    """
    def __init__(self, prototypeString):
        if re.search(CPPConstructor.getPattern(), prototypeString):
            self._match = re.search(CPPConstructor.getPattern(), prototypeString)
            self._name = self._match.group(1)
        else:
            raise ValueError("The given prototypeString is not a valid C++ constructor prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def __str__(self):
        return self._name

    @staticmethod
    def getPattern():
        return r'\s*(\w+)\(\)'


class CPPDestructor(object):
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
            self._match = re.search(CPPDestructor.getPattern(), prototypeString)
            self._name = self._match.group(1)
        else:
            raise ValueError("The given prototypeString is not a valid C++ destructor prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def __str__(self):
        return '~' + self._name

    @staticmethod
    def getPattern():
        return r'\s*~(\w+)\(\)'


class CPPEntitiesTester(unittest.TestCase):
    """Class to unit test al the CPPEntities."""
    def testCPPMethodPatternWithoutParameters(self):
        string = 'const std::string& getMessage() const'
        print(string)
        m = re.search(CPPMethod.getPattern(), string)
        self.assertTrue(m)
        print(m.group())

    def testCPPMethodPatternWithParameters(self):
        string = 'void setInteger(int integer)'
        print(string)
        m = re.search(CPPMethod.getPattern(), string)
        self.assertTrue(m)
        print(m.groups())

    def testCPPValuePatternForRef(self):
        string = 'const std::string&'
        print(string)
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m)
        print(m.groups())

    def testCPPValuePatternForPointer(self):
        string = 'const std::string*'
        print(string)
        m = re.search(CPPValue.getPattern(), string)
        print(m.groups())
        print(m.group())
        self.assertTrue(m.group(5))
        print(m.groups())

    def testCPPValuePatternForConst(self):
        string = 'conststring'
        print(string)
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m)
        print(m.groups())

    def testCPPValuePatternForVoid(self):
        string = 'void'
        print(string)
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m)
        print(m.groups())


if __name__ == '__main__':
    unittest.main()
