#!/usr/bin/env python
 
from distutils.core import setup
from distutils.extension import Extension

import distutils
distutils.log.set_verbosity(1)

VERSION = '0.1'

worker = Extension('worker', 
                    define_macros = [('PYTHON', '1')],
                    include_dirs = ['/usr/include/cppconn', '/usr/include/boost'],
                    libraries = ['mysqlcppconn', 'boost_python'],
                    sources = ['worker.cpp'])

setup (name = 'worker',
       version = VERSION,
       description = 'Performs business grunt work in c++ interacting directly with the db.',
       author = 'Samuel Colvin',
       author_email = 'S@muelColvin.com',
       long_description = '''
Performs business grunt work in c++ interacting directly with the db.
''',
       ext_modules = [worker])