#!/usr/bin/python
from cppentities import *


class PyAPIWriter(object):
    """ Object that can write both the pure C API and the Python wrapper
    corresponding to a given CPPClass. """
    def __init__(self, filename, includes, libraryName):
        """
        - filename is the core of the names of the files, without extension, to
        which the PyAPIWriter will write text. For instance, this could be 'myproject'.
        Then the C API would be written to 'myproject.h' and 'myproject.cpp';
        and the Python wrapper to 'myproject.py'.
        - includes is the list of header files that must be included in the C API header.
        - libraryName is the shared library of dll that will contain
        the bindings and hence that will be loaded by 'myproject.py'.
        """
        self._headerFilename = filename + '.h'
        self._implementationFilename = filename + '.cpp'
        self._wrapperFilename = filename + '.py'
        self._includes = includes
        self._libraryName = libraryName

    def writeClasses(self, classes):
        """ Main method of the class. Writes both the pure C API and the Python
        wrapper of the CPPClass collection 'classes' to the files. """
        print('PyAPIWriter: start writing classes...')
        self.initializeDeclaration()
        self.initializeImplementation()
        self.initializeWrapper()
        for class_ in classes:
            self._writeClass(class_)
        self.finalizeDeclaration()

    def _writeClass(self, class_):
        """ Writes the CPPClass 'class_' to the file in a C format and its
        corresponding Python wrapper. This method is for internal use (somehow private). """
        print("Writing class '" + class_.getName() +
            "' to files " + self._headerFilename +
            ", " + self._implementationFilename +
            " and " + self._wrapperFilename + ":")
        for constructor in class_.getConstructors():
            self.writeConstructor(constructor)

        if class_.hasDestructor():
            self.writeDestructor(class_.getDestructor())

        if class_.hasMethods():
            self.hadBlankLine(self._headerFilename)
            for method in class_.getMethods():
                self.writeMethod(class_.getName(), method)

    def initializeDeclaration(self):
        """ Adds its header to the C API header file. """
        with open(self._headerFilename, 'w') as f:
            f.write('/* File automatically generated by the pybindings project.\n'
                    'This file declare a pure C API for the C++ objects.\n'
                    'The following macros represent the standard way of making\n'
                    'exporting symbols from a DLL simpler. Linux part still to do. */\n'
                    '#ifdef PYBINDING_EXPORTS\n'
                    '#define PYBINDING_API __declspec(dllexport)\n'
                    '#else\n'
                    '#define PYBINDING_API __declspec(dllimport)\n'
                    '#endif\n\n')
            # Add the includes in alphabetical order.
            for include in sorted(self._includes):
                f.write('#include "' + include + '"\n')
            f.write('\nextern "C"\n'
                    '{\n')

    def finalizeDeclaration(self):
        """ Finalizes the file by closing braces etc. """
        with open(self._headerFilename, 'a') as f:
            f.write('}\n\n')

    def initializeImplementation(self):
        """ Adds its header to the C API implementation file. """
        with open(self._implementationFilename, 'w') as f:
            f.write('/* File automatically generated by the pybindings project.\n' +
                    'This file implements a pure C API for the C++ objects. */\n' +
                    '#include "' + self._headerFilename + '"\n\n' +
                    'static void nullObjectError(char* functionName)\n' +
                    '{\n' +
                    self.indent() + 'std::string message("*** ERROR ***\\nThe given object pointer is NULL in function ");\n' +
                    self.indent() + 'message += functionName;\n' +
                    self.indent() + 'std::cout << message.c_str() << std::endl;\n' +
                    '}\n\n')

    def initializeWrapper(self):
        """ Adds its header to the Python wrapper file. """
        with open(self._wrapperFilename, 'w') as f:
            f.write('#!/usr/bin/python\n'
                    '""" File automatically generated by the pybindings project.\n'
                    'This file implements a Python wrapper using ctypes for\n'
                    'the C++ objects exported in the ' + self._libraryName + ' library. """\n'
                    'from ctypes import *\n'
                    'lib = cdll.LoadLibrary(\'' + self._libraryName + '\')\n\n')

    def hadBlankLine(self, filename):
        """ Adds a blank line to the file corresponding to filename. """
        with open(filename, 'a') as f:
            f.write('\n')

    def writeConstructor(self, constructor):
        """ Writes the C API and the Python wrapper corresponding to the
        CPPConstructor 'constructor'. """
        print(self.indent() + 'Writing constructor...')

        # Handle declaration.
        constructorName = constructor.getName() + '_new'
        decl = constructorName + '('
        if constructor.hasParameters() > 0:
            decl = self.appendValuesToString(constructor.getParameters(), decl)
        decl += ')'
        with open(self._headerFilename, 'a') as f:
            f.write(self.indent() + constructor.getName() + '* ' + decl + ';\n')

        # Handle implementation.
        impl = ('PYBINDING_API void ' + constructor.getName() + '* ' + decl + '\n' +
                    '{\n' + self.indent() + 'return new ' + constructor.getName() + '(')
        if constructor.hasParameters():
            impl = self.appendValuesToString(constructor.getParameters(), impl)
        impl += ');\n}\n\n'
        with open(self._implementationFilename, 'a') as f:
            f.write(impl)

        # Handle wrapper.
        python = self.indent() + 'def __init__(self'
        # If necessary, get a list of the constructor parameters names and
        # append them to the wrapper __init__ string separated by commas.
        if constructor.hasParameters():
            parameterNames = [parameter.getName() for parameter in constructor.getParameters()]
            python += ', '
            python = self.appendValuesToString(parameterNames, python)
        python += ('):\n' +
                self.indent(2) + 'self._obj = lib.' + constructorName + '()\n\n')
        with open(self._wrapperFilename, 'a') as f:
            f.write(python)


    def writeDestructor(self, destructor):
        """ Writes the C API and the Python wrapper corresponding
        to the CPPDestructor 'destructor'. """
        print(self.indent() + 'Writing destructor...')
        # Handle declaration.
        destructorName = destructor.getName() + '_delete'
        decl = destructorName + '(' + destructor.getName() + '* obj)'
        with open(self._headerFilename, 'a') as f:
            f.write(self.indent() + 'void ' + decl + ';\n')

        # Handle implementation.
        impl = 'PYBINDING_API void ' + decl + '\n{\n' + self.indent()
        impl = self.appendNullObjectTestToString(impl)
        impl += '\n\n' + self.indent() + 'delete obj; obj = NULL;\n}\n\n'
        with open(self._implementationFilename, 'a') as f:
            f.write(impl)

        # Handle wrapper.
        python = (self.indent() + 'def __del__(self):\n' +
                self.indent(2) + 'lib.' + destructorName + '(self._obj)\n\n')
        with open(self._wrapperFilename, 'a') as f:
            f.write(python)


    def writeMethod(self, className, method):
        """ Writes the C API and the Python wrapper corresponding
        to the CPPMethod 'method'. """
        print(self.indent() + 'Writing method...')
        # Handle declaration.
        methodName = className + '_' + method.getName()
        decl = (str(method.getReturnValue()) + ' ' + methodName + '(' +
                className + '* obj')
        if method.hasParameters():
            decl += ', '
            decl = self.appendValuesToString(method.getParameters(), decl)
        decl += ')'
        with open(self._headerFilename, 'a') as f:
            f.write(self.indent() + decl + ';\n')

        # Handle implementation.
        impl = 'PYBINDING_API ' + decl + '\n{\n' + self.indent()
        impl = self.appendNullObjectTestToString(impl)
        impl += '\n\n' + self.indent() + 'return obj->' + method.getName() + '('
        parameterNames = []
        if method.hasParameters():
            # Make a list of the parameters names and
            # add them to 'impl' separated by commas.
            for parameter in method.getParameters():
                parameterNames.append(parameter.getName())
            impl = self.appendValuesToString(parameterNames, impl)
        impl += ');\n}\n\n'
        with open(self._implementationFilename, 'a') as f:
            f.write(impl)

        # Handle wrapper.
        python = self.indent() + 'def ' + method.getName() + '(self'
        # If necessary, get a list of the constructor parameters names and
        # append them to the wrapper string separated by commas.
        if method.hasParameters():
            parameterNames = [parameter.getName() for parameter in method.getParameters()]
            python += ', '
            python = self.appendValuesToString(parameterNames, python)
        python += '):\n' + self.indent(2) + 'lib.' + methodName + '(self._obj'
        # If necessary add the parameters to the implementation.
        if len(parameterNames) != 0:
            python += ', '
            python = self.appendValuesToString(parameterNames, python)
        python += ')\n\n'
        with open(self._wrapperFilename, 'a') as f:
            f.write(python)


    def appendValuesToString(self, values, string):
        """ Append the strings in 'values' to the 'string' in a function or
        method fashion. This means, all the values are separated from each othe
        by a comma and a space.  Remember strings are imutable, so in fact this
        method returns a new string with the appended values. """
        if len(values) == 0:
            raise Exception('The \'values\' collection must not be empty.')
        else:
            itValue = values.__iter__()
            value = itValue.next()
            while True:
                string += str(value)
                try:
                    value = itValue.next()
                except StopIteration:
                    break
                else:
                    string += ', '
        return string

    def appendNullObjectTestToString(self, string):
        """ Appends the null object function test to the string.
        Remember strings are imutable, so in fact returns a new
        string with the appended values. """
        string += 'if(obj == NULL) nullObjectError(__FUNCTION__);'
        return string

    def indent(self, count=1):
        """ Returns an indentation string corresponding to 'count',
        i.e., 4 spaces * count. By default, count is 1. """
        unitIndent = '    '
        return unitIndent * count

