import worker
connection = 'tcp://127.0.0.1:3306'
db_name = 'salesestimates'
user = 'sales-user'
password = ''
mysql = worker.MySQL(db_name, user, password, connection)
mysql.regenerate_csp()