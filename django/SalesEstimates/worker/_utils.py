import worker, settings
from time import time
def get_con():
    db = settings.DATABASES['default']
    sql_engine = 'django.db.backends.mysql'
    if db['ENGINE'] != sql_engine:
        raise Exception('Wrong DB in use, for c++ based worker MySQL (%s) is required.' % sql_engine)
    connection = 'tcp://%(HOST)s:%(PORT)s' % db
    mysql = worker.MySQL()
    msg = mysql.connect(db['NAME'], db['USER'], db['PASSWORD'], connection)
    return (mysql, msg)


def generate_skusales():
    start = time()
    mysql, msgs = get_con()
    msgs += mysql.generate_skusales()
    msgs += mysql.calculate_demand(settings.DEMAND_GROUPING, settings.GENERAL_LEAD_TIME)
    msgs += mysql.generate_orders()
    msgs += '\nTime taken: %0.3f seconds' % (time() - start)
    return msgs