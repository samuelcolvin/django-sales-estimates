#!../env/bin/python
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import SalesEstimates.worker as worker
import Imex.tasks as imex
import SalesEstimates.models as m
import Imex.models as imex_m
import pprint

def log(line):
    print line

class WorkerFuncs(object):
    @staticmethod
    def create_sales_periods(interactive):
        print 'Current number of sales Periods: %d' % m.SalesPeriod.objects.count()
        if interactive:
            response = raw_input('Are you sure you want to create sales periods? [y/n] ')
            if response.lower() != 'y':
                print 'exiting'
                return
        print ''
        worker.generate_sales_periods(WorkerFuncs._print)
        
#     @staticmethod
#     def populate_sales_periods(interactive):
#         worker.populate_sales_periods(WorkerFuncs._print)
        
    # TODO: this all needs fixing to work with the new imex app
    @staticmethod
    def import_from_xl(interactive):
        fname = 'CF sales estimates generated.xlsx'
#         fname =  raw_input('Enter file name (note: databaes will be cleared to accept new data): ')
        response = 'y'
        if interactive:
            response = raw_input('Clear database before importing from excel? [y/n] ')
        content = ImportExport.perform_import(fname, response.lower() == 'y')
        pprint.pprint(content)
        if 'success' in content:
            worker.generate_skusales(WorkerFuncs._print)
        
    @staticmethod
    def export_to_xl(interactive):
        processor = imex_m.Process.objects.create(action='EX')
        id = processor.id
        imex.perform_export(id)
        processor = imex_m.Process.objects.get(id=id)
        print 'TIME TAKEN: %0.3f' % processor.time_taken
        print 'LOG:\n%s' %  processor.log
        if processor.errors:
            print processor.errors
        
    @staticmethod
    def generate_sales_estimates(interactive):
        worker.generate_skusales(WorkerFuncs._print)
        
    @staticmethod
    def _print(line):
        print line
    
    @staticmethod
    def x_exit_without_doing_anything(interactive):
        if interactive:
            raw_input('About to exit, press enter to continue: ')
        print 'exitting'
        pass
        
useage = 'useage: python toolbox.py [function_name], where function_name can be found by running without an argument'
if len(sys.argv) == 1:
    i=1
    options={}
    print 'Choices:'
    for func in dir(WorkerFuncs):
        if not func.startswith('_'):
            options[i]=func
            print '%d >> %s' % (i, options[i])
            i+=1
    choice = input('\nEnter your choice of function to call by number: ')
    function_name = options[choice]
    interactive = True
elif len(sys.argv) == 2:
    function_name = sys.argv[1]
    interactive = False
else:
    print 'ERROR: arguments are wrong, system arguments: %s' % str(sys.argv)
    print useage
    sys.exit(2)
if not hasattr(WorkerFuncs, function_name):
    print 'ERROR: "%s" is not the name of an available function, call with no arguemtns to list available functions.' % function_name
    print useage
else:
    print '\n   ***calling %s, Interactive %r***\n' % (function_name, interactive)
    getattr(WorkerFuncs, function_name)(interactive)
