#!/usr/bin/python
import os
import platform


class PyAPIWriter(object):
    """
    Object that can write both the pure C API and the Python wrapper
    corresponding to a given CPPClass.

    The Python wrapper also contains some basic unit tests asserting that all
    the implemented methods can be executed without crashing. Note that this
    does not ensure that the code work properly, it only ensures that it
    can be executed.
    """
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

        # The unit tests are first written to a temporary file before being
        # concatenated in the main Python wrapper file.
        self._testerFilename = '__tester'

        # Counter of the number of constructors written to the C API files.
        self._writtenConstructors = 0

    def writeClasses(self, classes):
        """
        Main method of the class. Writes both the pure C API and the Python
        wrapper of the CPPClass collection 'classes' to the files.
        """
        print('PyAPIWriter: start writing classes...')
        self.initializeDeclaration()
        self.initializeImplementation()
        self.initializeWrapper()
        for class_ in classes:
            self._writeClass(class_)
        self.finalizeDeclaration()
        self.finalizeWrapper()

    def _writeClass(self, class_):
        """
        Writes the CPPClass 'class_' to the file in a C format and
        its corresponding Python wrapper. This method is for internal
        use (somehow private).
        """
        print("Writing class '" + class_.getName() +
            "' to files " + self._headerFilename +
            ", " + self._implementationFilename +
            " and " + self._wrapperFilename + ":")

        # First initialize the class implementation of the Python wrapper and of
        # its corresponding unit test class.
        with open(self._wrapperFilename, 'a') as f:
            f.write('class ' + class_.getName() + '(object):\n')
        with open(self._testerFilename, 'a') as f:
            f.write('class ' + class_.getName() + 'Tester(unittest.TestCase):\n')

        for constructor in class_.getConstructors():
            self.writeConstructor(constructor)

        if class_.hasDestructor():
            self.writeDestructor(class_.getDestructor())

        if class_.hasMethods():
            self.addBlankLine(self._headerFilename)
            for method in class_.getMethods():
                self.writeMethod(class_.getName(), method)

        # The class is totally implemented, now retrieve the unit tests that are
        # in the temporary file and put them in the wrapper file.
        self.concatenateTesterClass()

    def initializeDeclaration(self):
        """Add its header to the C API header file."""
        with open(self._headerFilename, 'w') as f:
            header = ('/* File automatically generated by the pybindings project.\n'
                    'This file declare a pure C API for the C++ objects.\n'
                    'The following macros allow to export the symbols from the ')
            if platform.system() == 'Windows':
                header += ('dll. */\n'
                        '#ifdef PYBINDING_EXPORTS\n'
                        '#define PYBINDING_API __declspec(dllexport)\n'
                        '#else\n'
                        '#define PYBINDING_API __declspec(dllimport)\n'
                        '#endif\n\n')
            else:
                header += ('shared library. */\n'
                        '#ifdef PYBINDING_EXPORTS\n'
                        '#define PYBINDING_API __attribute__((visibility("default")))\n'
                        '#else\n'
                        '#define PYBINDING_API\n'
                        '#endif\n\n')
            f.write(header)

            # Add the includes in alphabetical order.
            for include in sorted(self._includes):
                f.write('#include "' + include + '"\n')
            f.write('\nextern "C"\n'
                    '{\n')

    def finalizeDeclaration(self):
        """Finalize the file by closing braces etc."""
        with open(self._headerFilename, 'a') as f:
            f.write('}\n\n')

    def initializeImplementation(self):
        """Add its header to the C API implementation file."""
        with open(self._implementationFilename, 'w') as f:
            f.write('/* File automatically generated by the pybindings project.\n' +
                    'This file implements a pure C API for the C++ objects. */\n' +
                    '#include "' + self._headerFilename + '"\n\n' +
                    '#include <iostream>\n\n' +
                    'static void nullObjectError(char* functionName)\n' +
                    '{\n' +
                    self.indent() + 'std::string message("*** ERROR ***\\n"\n' +
                    self.indent(3) + '"The given object pointer is NULL in function ");\n' +
                    self.indent() + 'message += functionName;\n' +
                    self.indent() + 'std::cout << message.c_str() << std::endl;\n' +
                    '}\n\n')

    def initializeWrapper(self):
        """Add its header to the Python wrapper file."""
        with open(self._wrapperFilename, 'w') as f:
            f.write('#!/usr/bin/python\n'
                    '"""\nFile automatically generated by the pybindings project.\n'
                    'This file implements a Python wrapper using ctypes for\n'
                    'the C++ objects exported in the ' + self._libraryName + ' library.\n"""\n'
                    'import unittest\n'
                    'from ctypes import cdll\n'
                    'LIB = cdll.LoadLibrary(\'' + self._libraryName + '\')\n\n')

    def finalizeWrapper(self):
        """
        Finalize the Python wrapper implementation by adding an 'if main'
        statement running the unit tests.
        """
        self.addBlankLine(self._wrapperFilename)
        with open(self._wrapperFilename, 'a') as f:
            f.write('if __name__ == \'__main__\':\n' +
                    self.indent() + 'unittest.main()\n\n')

    def concatenateTesterClass(self):
        """
        Concatenate all the stuff that is in the temporary file containing
        the unit tests to the actual wrapper file.
        Then delete that temporary file.
        """
        self.addBlankLine(self._wrapperFilename)
        with open(self._wrapperFilename, 'a') as f:
            for line in open(self._testerFilename):
                f.write(line)
        os.remove(self._testerFilename)

    def addBlankLine(self, filename):
        """Add a blank line to the file corresponding to filename."""
        with open(filename, 'a') as f:
            f.write('\n')

    def writeConstructor(self, constructor):
        """
        Write the C API and the Python wrapper
        corresponding to the CPPConstructor 'constructor'.
        """
        print(self.indent() + 'Writing constructor...')

        # Handle declaration.
        # Since it is not possible to overload functions in ansi C, if there are
        # several constructors in the current class, they must all have
        # different names. So the constructors names will be:
        # <className>_new[_<number of the constructor in the file>]
        # Where the order of the constructor in the file is given by:
        # self._writtenConstructors
        constructorName = constructor.getName() + '_new'
        if self._writtenConstructors != 0:
            constructorName += '_' + str(self._writtenConstructors)
        self._writtenConstructors += 1

        decl = constructorName + '('
        if constructor.hasParameters() > 0:
            decl = self.appendValuesToString(constructor.getParameters(), decl)
        decl += ')'
        with open(self._headerFilename, 'a') as f:
            f.write(self.indent() + 'PYBINDING_API ' + constructor.getName() + '* ' + decl + ';\n')

        # Handle implementation.
        # FIXME make a list of the parameterNames as line 213 and pass it to the
        # implementation.
        impl = (constructor.getName() + '* ' + decl + '\n' +
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
                self.indent(2) + 'self._obj = LIB.' + constructorName + '()\n\n')
        with open(self._wrapperFilename, 'a') as f:
            f.write(python)

        # Handle unit test.
        python = (self.indent() + 'def testConstructor(self):\n' +
                self.indent(2) + 'obj = ' + constructor.getName() + '()\n' +
                self.indent(2) + 'self.assertTrue(obj)\n\n')
        with open(self._testerFilename, 'a') as f:
            f.write(python)

    def writeDestructor(self, destructor):
        """
        Write the C API and the Python wrapper
        corresponding to the CPPDestructor 'destructor'.
        """
        print(self.indent() + 'Writing destructor...')
        # Handle declaration.
        destructorName = destructor.getName() + '_delete'
        decl = 'void ' + destructorName + '(' + destructor.getName() + '* obj)'
        with open(self._headerFilename, 'a') as f:
            f.write(self.indent() + 'PYBINDING_API ' + decl + ';\n')

        # Handle implementation.
        impl = 'void ' + decl + '\n{\n' + self.indent()
        impl = self.appendNullObjectTestToString(impl)
        impl += '\n\n' + self.indent() + 'delete obj; obj = NULL;\n}\n\n'
        with open(self._implementationFilename, 'a') as f:
            f.write(impl)

        # Handle wrapper.
        python = (self.indent() + 'def __del__(self):\n' +
                self.indent(2) + 'LIB.' + destructorName + '(self._obj)\n\n')
        with open(self._wrapperFilename, 'a') as f:
            f.write(python)

        # Handle unit test.
        python = (self.indent() + 'def testDestructor(self):\n' +
                self.indent(2) + 'obj = ' + destructor.getName() + '()\n' +
                self.indent(2) + 'self.assertTrue(obj)\n' +
                self.indent(2) + 'obj.__del__()\n' +
                self.indent(2) + 'self.assertFalse(obj)\n\n')
        with open(self._testerFilename, 'a') as f:
            f.write(python)


    def writeMethod(self, className, method):
        """
        Write the C API and the Python wrapper
        corresponding to the CPPMethod 'method'.
        """
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
            f.write(self.indent() + 'PYBINDING_API ' + decl + ';\n')

        # Handle implementation.
        impl = decl + '\n{\n' + self.indent()
        impl = self.appendNullObjectTestToString(impl)
        impl += '\n\n' + self.indent()
        # If there is non-void return value, add the 'return' statement
        # to the implementation string.
        if method.getReturnValue().getType() != 'void':
            impl += 'return '
        impl += 'obj->' + method.getName() + '('
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
        python += '):\n' + self.indent(2)
        # If there is non-void return value, add the 'return' statement
        # to the wrapper string.
        if method.getReturnValue().getType() != 'void':
            python += 'return '
        python += 'LIB.' + methodName + '(self._obj'
        # If necessary add the parameters to the implementation.
        if len(parameterNames) != 0:
            python += ', '
            python = self.appendValuesToString(parameterNames, python)
        python += ')\n\n'
        with open(self._wrapperFilename, 'a') as f:
            f.write(python)

        # Handle unit test.
        python = (self.indent() + 'def test_' + method.getName() + '(self):\n' +
                self.indent(2) + 'obj = ' + className + '()\n' +
                self.indent(2) + 'self.assertTrue(obj)\n' +
                self.indent(2) + 'obj.' + method.getName() + '()\n' +
                self.indent(2) + 'self.assertTrue(obj)\n\n')
        with open(self._testerFilename, 'a') as f:
            f.write(python)

    def appendValuesToString(self, values, string):
        """Append the strings in 'values' to the 'string' in a function or
        method parameter definition fashion.

        This means, all the values are separated from each othe
        by a comma and a space.  Remember strings are imutable, so in fact this
        method returns a new string with the appended values.
        """
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
        """Append the null object function test to the string.

        Remember that strings are imutable, so in fact returns a new
        string with the appended values.
        """
        string += 'if(obj == NULL) nullObjectError(__FUNCTION__);'
        return string

    def indent(self, count=1):
        """Return an indentation string corresponding to 'count',
        i.e., 4 spaces * count. By default, count is 1.
        """
        unitIndent = '    '
        return unitIndent * count

