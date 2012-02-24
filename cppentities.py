#!/usr/bin/python
import re


class CPPClass(object):
    """A whole C++ class with all its potential constructors, methods and destructor."""
    def __init__(self, className):
        self._className = className
        self._entities = {'constructors': [],
                            'destructor': None,
                            'methods': []}

    def getName(self):
        return self._className

    def addConstructor(self, constructor):
        self._entities['constructors'].append(constructor)

    def addDestructor(self, destructor):
        self._entities['destructor'] = destructor

    def addMethod(self, method):
        self._entities['methods'].append(method)

    def __str__(self):
        string = ''
        for constructor in self._entities['constructors']:
            string += str(constructor) + '\n'
        string += str(self._entities['destructor']) + '\n'
        for method in self._entities['methods']:
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
            self._entities = {'const': False,
                                'namespace': None,
                                'type': None,
                                'reference': False,
                                'pointer': False}

            self._entities['const'] = self._match.group(1)
            if self._match.group(3):
                self._entities['namespace'] = self._match.group(2)
                self._entities['type'] = self._match.group(4)
                self._entities['reference'] = (self._match.group(5) == '&')
                self._entities['pointer'] = (self._match.group(5) == '*')
            else:
                self._entities['namespace'] = None
                self._entities['type'] = self._match.group(2)
                self._entities['reference'] = (self._match.group(3) == '&')
                self._entities['pointer'] = (self._match.group(3) == '*')
        else:
            raise ValueError("The given prototypeString is not a valid C++ value.")

    def getMatchedGroups(self):
        return self._match.groups()

    def isConst(self):
        return self._entities['const']

    def getNamespace(self):
        return self._entities['namespace']

    def getType(self):
        return self._entities['type']

    def isReference(self):
        return self._entities['reference']

    def isPointer(self):
        return self._entities['pointer']

    def __str__(self):
        return (str(self.isConst()) + ' ' + str(self.getNamespace()) + ' ' +
        str(self.getType()) + ' ' + str(self.isReference() or self.isPointer()))

    @staticmethod
    def getPattern():
        return r'(const)?\s+(\w+)(::)?(\w+)?\s*(&\|*)?'

    @staticmethod
    def getPatternWithoutGroups():
        return r'(?:const)?\s+\w+(?:::)?(?:\w+)?\s*(?:&\|*)?'


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
            self._entities = {'returnValue': None,
                                'name': ''}
            # The first group is a CPPValue so build it.
            self._entities['returnValue'] = CPPValue(self._match.group(1))
            self._entities['name'] = self._match.group(2)
        else:
            raise ValueError("The given prototypeString is not a valid C++ method prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def getReturnValue(self):
        return self._entities['returnValue']

    def getName(self):
        return self._entities['name']

    def __str__(self):
        return str(self.getReturnValue()) + ' ' + self.getName()

    @staticmethod
    def getPattern():
        return r'\/\^\s*(' + CPPValue.getPatternWithoutGroups() + r')\s+(\w+)'


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
            self._className = self._match.group(1)
        else:
            raise ValueError("The given prototypeString is not a valid C++ constructor prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    def __str__(self):
        return self._className

    @staticmethod
    def getPattern():
        return r'\/\^\s*(\w+)\(\)'


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
        return r'\/\^\s*~(\w+)\(\)'
