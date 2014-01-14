#include <stdlib.h>
#include <iostream>

/*
  Include directly the different
  headers from cppconn/ and mysql_driver.h + mysql_util.h
  (and mysql_connection.h). This will reduce your build time!
*/
//#include "mysql_connection.h"

#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>

using namespace std;

int connect(void)
{
    cout << endl;
    cout << "Running 'SELECT 'Hello World!' » AS _message'..." << endl;

	try {
	  sql::Driver *driver;
	  sql::Connection *con;
	  sql::Statement *stmt;
	  sql::ResultSet *res;

	  /* Create a connection */
	  driver = get_driver_instance();
	  con = driver->connect("tcp://127.0.0.1:3306", "sales-user", "");
	  /* Connect to the MySQL test database */
	  con->setSchema("salesestimates");

	  stmt = con->createStatement();
	  string query = "SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;";
	  cout << "executing: " << query << endl;
	  res = stmt->executeQuery(query);
	  while (res->next()) {
		cout << "response:        " << res->getInt(1) << endl;
	  }
	  query = "TRUNCATE TABLE SalesEstimates_customersalesperiod;";
	  cout << "executing: " << query << endl;
	  stmt->executeQuery(query);
	  delete res;
	  delete stmt;
	  delete con;

	} catch (sql::SQLException &e) {
	  cout << "# ERR: SQLException in " << __FILE__;
	  cout << "(" << __FUNCTION__ << ") on line " << __LINE__ << endl;
	  cout << "# ERR: " << e.what();
	  cout << " (MySQL error code: " << e.getErrorCode();
	  cout << ", SQLState: " << e.getSQLState() << " )" << endl;
	}

	cout << endl;

	return EXIT_SUCCESS;
}

void say_hello(const char* name) {
    cout << "Hello " <<  name << "!\n";
}


#ifdef PYTHON

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
using namespace boost::python;

BOOST_PYTHON_MODULE(worker)
{
    def("connect", connect);
    def("say_hello", say_hello);
}
#else

int main(int, char*[])
{
	connect();
}
#endif
