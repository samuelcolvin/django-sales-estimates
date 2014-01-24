#!../../../env/bin/python
import unittest, sys, os, traceback
sys.path.insert(0,'build/lib.linux-x86_64-2.7/')
sys.path.insert(0, '../../')
import worker, settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import SalesEstimates.models as m

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        connection = 'tcp://127.0.0.1:3306'
        db_name = 'salesestimates'
        user = 'sales-user'
        password = ''
        self.mysql = worker.MySQL()
        print self.mysql.connect(db_name, user, password, connection)
    
    def tearDown(self):
        if hasattr(self, 'customer'):
            print 'deleting customer: %r' % self.customer
            self.customer.delete()

#     def test_clear_generate(self):
#         print self.mysql.clear_csp()
#         print self.mysql.generate_csp()
#     
#     def test_customer_setup(self):
#         first_store_count = 6
#         second_store_count = 10
#         self.customer = m.Customer.objects.create(name='test customer', dft_store_count=first_store_count)
#         csp_count1 = m.CustomerSalesPeriod.objects.count()
#         sales_period_count = m.SalesPeriod.objects.count()
#         print 'looking up customer %r with id %d' % (self.customer.name, self.customer.id)
#         print self.mysql.add_customer_csp(self.customer.id)
#         csp_count2 = m.CustomerSalesPeriod.objects.count()
#         self.assertTrue(csp_count2 == (csp_count1 + sales_period_count))
#         new_csps = m.CustomerSalesPeriod.objects.filter(customer = self.customer)
#         self.assertTrue(len([csp for csp in new_csps if csp.store_count != first_store_count]) == 0)
#         new_csps[0].custom_store_count = True
#         new_csps[0].save()
#         new_csps[1].store_count = 1
#         new_csps[1].save()
#         self.customer.dft_store_count = second_store_count
#         self.customer.save()
#         print self.mysql.update_cust_csp(self.customer.id)
#         new_csps2 = m.CustomerSalesPeriod.objects.filter(customer = self.customer)
#         non_standard_sc = len([csp for csp in new_csps2 if csp.store_count != second_store_count])
#         print 'non standard store count, count: %d' % non_standard_sc
#         self.assertTrue(non_standard_sc == 2)

    def test_generate_skus(self):
     	print self.mysql.generate_skusales()
        print self.mysql.calculate_demand(settings.DEMAND_GROUPING, settings.GENERAL_LEAD_TIME)
        print self.mysql.generate_orders()
    
#     def test_date_arith(self):
#         print self.mysql.test_date_arith()

if __name__ == '__main__':
    unittest.main()
