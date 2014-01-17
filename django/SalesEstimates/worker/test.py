import unittest
import worker
mysql = worker.MySQL()

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        connection = 'tcp://127.0.0.1:3306'
        db_name = 'salesestimates'
        user = 'sales-user'
        password = ''
        self.mysql = worker.MySQL()
        print self.mysql.connect(db_name, user, password, connection)

    def test_clear_generate(self):
        print self.mysql.clear_csp()
        print self.mysql.generate_csp()
        
#         self.assertEqual(self.seq, range(10))
#         # should raise an exception for an immutable sequence
#         self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()