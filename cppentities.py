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
            self._name = ''

            # Handle the const character of the cpp value.
            if self._match.group(1):
                self._const = True

            if self._match.group(3):
                # This means that the current cpp value has a namespace.
                self._namespace = self._match.group(2)
                self._type = self._match.group(4)
            else:
                # Here the current cpp value doesn't have a namespace.
                self._namespace = None
                self._type = self._match.group(2)

            self._reference = (self._match.group(5) == '&')
            self._pointer = (self._match.group(5) == '*')
            self._name = self._match.group(6)
        else:
            raise ValueError("The given prototypeString is not a valid C++ value.")

    def getMatchedGroups(self):
        return self._match.groups()

    def isConst(self):
        return self._const

    def hasNamespace(self):
        return bool(self._namespace)

    def getNamespace(self):
        if self.hasNamespace:
            return self._namespace
        else:
            return ''

    def getType(self):
        return self._type

    def isReference(self):
        return self._reference

    def isPointer(self):
        return self._pointer

    def getName(self):
        return self._name

    def toJSON(self):
        j = {'const': self.isConst(),
            'namespace': self.getNamespace(),
            'type': self.getType(),
            'reference': self.isReference(),
            'pointer': self.isPointer(),
            'name': self._name}
        return j

    def __str__(self):
        return str(self.toJSON())

    @staticmethod
    def getPattern():
        # The group will match 'const ', don't forget to strip it.
        return r'\s*(const )?\s*(\w+)(::)?(\w+)?\s*(\&|\*)?\s*(\w+)?'
        #(a)?(?<!a)((?:\s+|b)+)

    @staticmethod
    def getPatternWithoutGroups():
        # The group will match 'const ', don't forget to strip it.
        return r'\s*(?:const )?\s*\w+(?:::)?(?:\w+)?\s*(?:\&|\*)?\s*(?:\w+)?'


class CPPMethod(object):
    """
    CPPMethod represents a C++ method generic prototype.
    For the moment, template methods are not handled.
    A C++ method is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field has the tag '?'
    So:
    [const]? [namespace]? [return value] [reference or pointer]? [method name] [parameters]? [const]?
    """
    def __init__(self, prototypeString):
        if re.search(CPPMethod.getPattern(), prototypeString):
            self._match = re.search(CPPMethod.getPattern(), prototypeString)

            # Set default values.
            self._returnValue = None
            self._name = ''
            self._parameters = []
            self._const = False

            # The first group is the return value of the cpp method,
            # so build it as a CPPValue.
            self._returnValue = CPPValue(self._match.group(1))

            # Then the name of the method itself.
            self._name = self._match.group(2)

            # The third group is the string found inside
            # the parenthesis of the method prototype. So if this
            # group is True, it contains the parameters of the
            # method, hence build the corresponding CPPValue's if necessary.
            if self._match.group(3):
                # Replace the commas of the parameters by spaces if necessary.
                # Then try to match as much as CPPValue's as possible.
                values = re.findall(CPPValue.getPatternWithoutGroups(),
                    self._match.group(3).replace(',', ' '))
                for value in values:
                    self._parameters.append(CPPValue(value))

            # Handle the const character of the method.
            if self._match.group(4):
                self._const = True
        else:
            raise ValueError("The given prototypeString is not a valid C++ method prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def getReturnValue(self):
        return self._returnValue

    def getName(self):
        return self._name

    def isConst(self):
        return self._const

    def getParameters(self):
        return self._parameters

    def toJSON(self):
        j = {'return': self.getReturnValue(),
            'name': self.getName(),
            'parameters': self.getParameters()}
        return j

    def __str__(self):
        msg = str(self.getReturnValue()) + ' ' + self.getName() + ' '
        for parameter in self._parameters:
            msg += str(parameter) + ' '
        msg += str(self._const)
        return msg

    @staticmethod
    def getPattern():
        return (r'\s*(' +
            CPPValue.getPatternWithoutGroups() +
            r')\s+(\w+)\s*\((.+)?\)\s*(const)?')


class CPPConstructor(object):
    """
    CPPConstructor represents a C++ method generic constructor.
    A C++ constructor is defined with the following fields:
    - A field is delimited by square braces '[]'
    - An optional field has the tag '?'
    So:
    [class name] [parameters]?
    """
    def __init__(self, prototypeString):
        if re.search(CPPConstructor.getPattern(), prototypeString):
            self._match = re.search(CPPConstructor.getPattern(), prototypeString)

            # The first group is the name of the class.
            self._name = self._match.group(1)

            # The second group is the string found inside
            # the parenthesis of the constructor prototype.
            # So if this group is True, it contains the
            # parameters of the constructor, hence build
            # the corresponding CPPValue's if necessary.
            self._parameters = []
            if self._match.group(2):
                # Replace the commas of the parameters by spaces if necessary.
                # Then try to match as much as CPPValue's as possible.
                values = re.findall(CPPValue.getPatternWithoutGroups(),
                    self._match.group(2).replace(',', ' '))
                for value in values:
                    self._parameters.append(CPPValue(value))

            # Now check if this is a copy constructor.
            # Only one parameter, const ref with the name of the class?
            if (len(self._parameters) == 1 and
                self._parameters[0].getType() == self._name and
                self._parameters[0].isConst() and
                self._parameters[0].isReference()):
                self._isCopyConstructor = True
            else:
                self._isCopyConstructor = False
        else:
            raise ValueError("The given prototypeString is not a valid C++ constructor prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def getName(self):
        return self._name

    def getParameters(self):
        return self._parameters

    def isCopyConstructor(self):
        return self._isCopyConstructor

    def toJSON(self):
        j = {'name': self.getName(),
            'parameters': self.getParameters(),
            'iscopyconstructor': self.isCopyConstructor()}
        return j

    def __str__(self):
        msg = self.getName() + ' '
        for parameter in self._parameters:
            msg += str(parameter) + ' '
        return msg

    @staticmethod
    def getPattern():
        return r'\s*(\w+)\((.+)?\)'


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
        m = re.search(CPPMethod.getPattern(), string)
        self.assertTrue(m)

    def testCPPMethodPatternWithParameter(self):
        string = 'void setInteger(int integer)'
        m = re.search(CPPMethod.getPattern(), string)
        self.assertTrue(m)

    def testCPPValuePatternForRef(self):
        string = 'const std::string&'
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m)
        self.assertTrue(m.group(5) == '&')

    def testCPPValuePatternForPointer(self):
        string = 'const std::string*'
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m.group(5) == '*')

    def testCPPValuePatternForConst(self):
        string = 'conststring'
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m)
        self.assertFalse(m.group(1))

    def testCPPValuePatternForVoid(self):
        string = 'void'
        m = re.search(CPPValue.getPattern(), string)
        self.assertTrue(m)
        self.assertFalse(m.group(1))
        self.assertFalse(m.group(4))

    def testCPPValueForPointer(self):
        string = 'const std::string * myStr'
        value = CPPValue(string)
        self.assertTrue(value)
        self.assertTrue(value.isPointer())
        self.assertFalse(value.isReference())
        self.assertTrue(value.getName() == 'myStr')

    def testCPPValueFor3Pointers(self):
        string = 'const string ** * myStr'
        value = CPPValue(string)
        self.assertTrue(value)
        self.assertTrue(value.isPointer())
        self.assertFalse(value.isReference())
        self.assertTrue(value.getName() == 'myStr')

    def testCPPValueForReference(self):
        string = 'const std::string &myStr'
        value = CPPValue(string)
        self.assertTrue(value)
        self.assertFalse(value.isPointer())
        self.assertTrue(value.isReference())
        self.assertTrue(value.getName() == 'myStr')

    def testCPPValueForReference2(self):
        string = 'string &myStr'
        value = CPPValue(string)
        self.assertTrue(value)
        self.assertFalse(value.isPointer())
        self.assertTrue(value.isReference())
        self.assertTrue(value.getName() == 'myStr')

    def testCPPValueForCopy(self):
        string = 'const std::string  myStr'
        value = CPPValue(string)
        self.assertTrue(value)
        self.assertFalse(value.isPointer())
        self.assertFalse(value.isReference())
        self.assertTrue(value.getName() == 'myStr')

    def testCPPMethod(self):
        string = 'const std::string* doSomething(const Object& obj, std::string* str) const'
        method = CPPMethod(string)
        self.assertTrue(method)

    def testCPPConstructor(self):
        string = 'Object(const Stuff& obj, std::string* str)'
        constructor = CPPConstructor(string)
        self.assertTrue(constructor)
        self.assertTrue(len(constructor.getParameters()) == 2)
        self.assertFalse(constructor.isCopyConstructor())

    def testCPPConstructorIsNotCopyConstructor(self):
        string = 'Object(const Stuff& obj)'
        constructor = CPPConstructor(string)
        self.assertTrue(constructor)
        self.assertFalse(constructor.isCopyConstructor())

    def testCPPConstructorIsCopyConstructor(self):
        string = 'Object(const Object& obj)'
        constructor = CPPConstructor(string)
        self.assertTrue(constructor)
        self.assertTrue(constructor.isCopyConstructor())

if __name__ == '__main__':
    unittest.main()
