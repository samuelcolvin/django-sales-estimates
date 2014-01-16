import worker
connection = 'tcp://127.0.0.1:3306'
db_name = 'salesestimates'
user = 'sales-user'
password = ''
mysql = worker.MySQL()
print mysql.connect(db_name, user, password, connection)
print mysql.clear_csp()
print mysql.generate_csp()

