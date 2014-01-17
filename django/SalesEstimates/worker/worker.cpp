#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <vector>

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
	vector<int> _get_sales_periods();
  public:
	string connect(string, string, string, string);

	// to generate a whole set of sales periods (may require entire reset), to add extra sales periods
	string regenerate_sales_periods();
	string extend_sales_periods();

	// to clear and generate the customer sales periods
	string clear_csp();
	string generate_csp();

	// to add all the csp's for a new customer, and update their store count for an existing one
	string add_customer_csp(int);
	string update_cust_csp(int);
};

string MySQL::connect(string db_name, string user, string password, string connection)
{
	ostringstream stream;
	sql::Driver *driver;

	driver = get_driver_instance();
	con = driver->connect(connection, user, password);
	con->setSchema(db_name);
	stream << "Successfully connected to " << connection << " > " << db_name;
	return stream.str();
}

vector<int> MySQL::_get_sales_periods()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	vector<int> sales_periods;
	res = stmt->executeQuery("SELECT id FROM SalesEstimates_salesperiod;");
	while (res->next()) {
		sales_periods.push_back(res->getInt("id"));
	}
	return sales_periods;
}

string MySQL::clear_csp()
{
	ostringstream stream;
	sql::Statement *stmt;
	sql::ResultSet *res;

	stmt = con->createStatement();
	res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;");
	res->next();
	stream << "Deleting " << res->getInt(1) << " Customer Sales Period Records";
	stmt->execute("DELETE FROM SalesEstimates_customersalesperiod;");
	return stream.str();
}

string MySQL::generate_csp()
{
	ostringstream stream;
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	vector<int> sales_periods = _get_sales_periods();

	res = stmt->executeQuery("SELECT id, dft_store_count FROM SalesEstimates_customer;");
	ostringstream query_stream;
	query_stream << "INSERT INTO SalesEstimates_customersalesperiod(customer_id, period_id, store_count) VALUES";
	bool first_set = true;
	int cust_id, store_cnt;
	int add_count = 0;
	while (res->next()) {
		for(vector<int>::iterator pid = sales_periods.begin(); pid != sales_periods.end(); ++pid)
		{
			if (!first_set)
				query_stream << ",";
			first_set = false;
			cust_id = res->getInt("id");
			store_cnt = res->getInt("dft_store_count");
			query_stream << "(" << cust_id << "," << *pid << "," << store_cnt << ")";
			add_count++;
		}
	}
	query_stream << ";";
	stmt->execute(query_stream.str());
	stream << "Added " << add_count << " Customer Sales Period Records";

	delete res;
	delete stmt;
	return stream.str();
}

string MySQL::add_customer_csp(int cust_id)
{
	ostringstream stream;
	sql::Statement *stmt;
	sql::ResultSet *res;
	sql::PreparedStatement *pstmt;
	stmt = con->createStatement();
	vector<int> sales_periods = _get_sales_periods();

	pstmt = con->prepareStatement("SELECT name, dft_store_count FROM SalesEstimates_customer WHERE id=?;");
	pstmt->setInt(1, cust_id);
	res = pstmt->executeQuery();
	res->next();
	string name = res->getString("name");
	int store_count = res->getInt("dft_store_count");
	stream << "Updating  " << name << " with store count: " << store_count << endl;
	ostringstream query_stream;
	query_stream << "INSERT INTO SalesEstimates_customersalesperiod(customer_id, period_id, store_count) VALUES";
	bool first_set = true;
	int add_count = 0;
	while (res->next()) {
		for(vector<int>::iterator pid = sales_periods.begin(); pid != sales_periods.end(); ++pid)
		{
			if (!first_set)
				query_stream << ",";
			first_set = false;
			query_stream << "(" << cust_id << "," << *pid << "," << store_count << ")";
			add_count++;
		}
	}
	query_stream << ";";
	stmt->execute(query_stream.str());
	stream << "Added " << add_count << " Customer Sales Period Records";

	delete pstmt;
	delete res;
	delete stmt;
	return stream.str();
}

//	sql::PreparedStatement *pstmt;
//	pstmt = con->prepareStatement("INSERT INTO SalesEstimates_customersalesperiod(customer_id, period_id, store_count) VALUES (?, ?, ?)");
//	while (res->next()) {
//		cout << "id: " << res->getInt("id") << ", name: " << res->getString("name") << endl;
//		for (int spi= 0; spi < sales_periods; spi++)
//		{
//			pstmt->setInt(1, res->getInt("id"));
//			pstmt->setInt(2, sales_period_ids[spi]);
//			pstmt->setInt(3, res->getInt("dft_store_count"));
//			pstmt->execute();
//		}
//	}
//	delete pstmt;

#ifdef PYTHON

#include <boost/python/module.hpp>
//#include <boost/python/def.hpp>
#include <boost/python.hpp>
using namespace boost::python;

BOOST_PYTHON_MODULE(worker)
{
    class_<MySQL>("MySQL")
        .def("connect", &MySQL::connect)
        .def("generate_csp", &MySQL::generate_csp)
        .def("clear_csp", &MySQL::clear_csp)
        .def("add_customer_csp", &MySQL::add_customer_csp)
    ;
}
#else

int main(int, char*[])
{
	connect();
}
#endif
