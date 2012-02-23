#!/usr/bin/python
import re


class CPPClass(object):
    """A whole C++ class with all its potential constructors, methods and destructor."""
    def __init__(self, entities):
        raise NotImplementedError


class CPPValue(object):
    """
    CPPValue represents a C++ value type,
    that is, a type and its attributes (const and/or pointer or reference).
    """
    def __init__(self, valueString):
        pass

    @staticmethod
    def getPattern():
        return r'(const)?\s+(\w+)(::)?(\w+)?\s*(&\|*)?'


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
            print('Building a CPPMethod.')
            self._match = re.search(CPPMethod.getPattern(), prototypeString)
        else:
            raise ValueError("The given prototypeString is not a valid C++ method prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    @staticmethod
    def getPattern():
        return r'\/\^\s*' + CPPValue.getPattern() + r'\s+(\w+)'


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
            print('Building a CPPConstructor.')
            self._match = re.search(CPPConstructor.getPattern(), prototypeString)
            self._className = self._match.group(1)
        else:
            raise ValueError("The given prototypeString is not a valid C++ constructor prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

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
            print('Building a CPPDestructor.')
            self._match = re.search(CPPDestructor.getPattern(), prototypeString)
        else:
            raise ValueError("The given prototypeString is not a valid C++ destructor prototype.")

    def getMatchedGroups(self):
        return self._match.groups()

    @staticmethod
    def getPattern():
        return r'\/\^\s*~(\w+)\(\)'
