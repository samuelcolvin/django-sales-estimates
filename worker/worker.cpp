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
#include <cppconn/prepared_statement.h>

using namespace std;

class MySQL {
	sql::Connection *con;
  public:
	MySQL(string, string, string, string);
    int regenerate_csp();
};

MySQL::MySQL(string db_name, string user, string password, string connection)
{
	sql::Driver *driver;

	driver = get_driver_instance();
	con = driver->connect(connection, user, password);
	con->setSchema(db_name);
	cout << "Successfully connected to " << connection << " > " << db_name << endl;
}


int MySQL::regenerate_csp()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	sql::PreparedStatement *pstmt;

	stmt = con->createStatement();
	string query = "SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;";
	cout << "executing: " << query << endl;
	res = stmt->executeQuery(query);
	res->next();
	cout << "Records: " << res->getInt(1) << endl;
	query = "DELETE FROM SalesEstimates_customersalesperiod;";
	cout << "executing: " << query << endl;
	query = "SELECT COUNT(*) FROM SalesEstimates_salesperiod;";
	cout << "executing: " << query << endl;
	res = stmt->executeQuery(query);
	res->next();
	int sales_periods = res->getInt(1);
	int sales_period_ids[sales_periods];
	query = "SELECT id FROM SalesEstimates_salesperiod;";
	cout << "executing: " << query << endl;
	res = stmt->executeQuery(query);
	int i = 0;
	while (res->next()) {
	  sales_period_ids[i] = res->getInt("id");
	  i++;
	}

	query = "SELECT id, name, dft_store_count FROM SalesEstimates_customer;";
	cout << "executing: " << query << endl;
	res = stmt->executeQuery(query);
	pstmt = con->prepareStatement("INSERT INTO SalesEstimates_customersalesperiod(customer_id, period_id, store_count) VALUES (?, ?, ?)");
	while (res->next()) {
		cout << "id: " << res->getInt("id") << ", name: " << res->getString("name") << endl;
		for (int spi= 0; spi < sales_periods; spi++)
		{
			pstmt->setInt(1, res->getInt("id"));
			pstmt->setInt(2, sales_period_ids[spi]);
			pstmt->setInt(3, res->getInt("dft_store_count"));
			pstmt->executeUpdate();
		}
	}
	delete pstmt;
	delete res;
	delete stmt;
	return 1;
}

#ifdef PYTHON

#include <boost/python/module.hpp>
//#include <boost/python/def.hpp>
#include <boost/python.hpp>
using namespace boost::python;

BOOST_PYTHON_MODULE(worker)
{
    class_<MySQL>("MySQL", init<string, string, string, string>())
        .def("regenerate_csp", &MySQL::regenerate_csp)
    ;
}
#else

int main(int, char*[])
{
	connect();
}
#endif
