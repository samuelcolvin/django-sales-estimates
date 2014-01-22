#!/usr/bin/env python
 
from distutils.core import setup
from distutils.extension import Extension

import distutils
distutils.log.set_verbosity(1)

import os
from distutils.sysconfig import get_config_vars

remove_flag = ['-Wstrict-prototypes']
os.environ['OPT'] = " ".join(
    flag for flag in get_config_vars('OPT')[0].split() if flag not in remove_flag
)

VERSION = '0.1'

worker = Extension('worker', 
                    define_macros = [('PYTHON', '1')],
                    include_dirs = ['/usr/include/cppconn', '/usr/include/boost'],
                    libraries = ['mysqlcppconn', 'boost_python'],
                    sources = ['worker.cpp', 'worker_extra.cpp'],
                    extra_compile_args = ['-std=c++11'])

setup (name = 'worker',
       version = VERSION,
       description = 'Performs business grunt work in c++ interacting directly with the db.',
       author = 'Samuel Colvin',
       author_email = 'S@muelColvin.com',
       long_description = '''
Performs business grunt work in c++ interacting directly with the db.
''',
       ext_modules = [worker])