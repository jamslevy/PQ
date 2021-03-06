#!/usr/bin/env python
import os
import unittest
from optparse import OptionParser
     
def run_tests(verbosity):
    """
    PyUnit Test runner suitable for use with Google App Engine.
    Drop this file into your project directory, create a directory called tests in the same 
    directory and create a blank file in that called __init__.py
    You directory structure should be something like this:
    
      - root
        - app.yaml
        - main.py
        - test.py
        - tests
          - __init__.py
        
    You should now be able to just drop valid PyUnit test cases into the tests
    directory and they should be run when you run test.py via the command line.
    """
    
    # list all the files in the tests directory
    file_list = os.listdir(os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), 'tests'))
    test_modules = []
    # loop over all the file names
    for file_name in file_list:
        extension = os.path.splitext(file_name)[-1]
        # if they are python files
        if extension == '.py':
            # work out the module name
            test_module_name = "tests." + os.path.splitext(file_name)[0:-1][0]
            # now import the module
            module = __import__(test_module_name, globals(), locals(), test_module_name)
            # and add it to the list of available modules
            test_modules.append(module)
        
    # populate a test suite from the individual tests from the list of modules
    suite = unittest.TestSuite(map(unittest.defaultTestLoader.loadTestsFromModule, test_modules))
    # set up the test runner
    runner = unittest.TextTestRunner(verbosity=int(verbosity))
    # run the tests
    runner.run(suite)
    
if __name__ == '__main__':
    # instantiate the arguments parser
    parser = OptionParser()
    # add an option so we can set the test runner verbosity
    parser.add_option('--verbosity', action='store', dest='verbosity', default='1',
                          type='choice', choices=['0', '1', '2'],
                          help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
    # parse the command arguments
    (options, args) = parser.parse_args()
        
    # run the tests with the passed verbosity
    run_tests(options.verbosity)
