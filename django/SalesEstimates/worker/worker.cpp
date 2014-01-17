#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <vector>
#include <time.h>

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

#ifdef PYTHON

#include <boost/python/module.hpp>
//#include <boost/python/def.hpp>
#include <boost/python.hpp>
using namespace boost::python;
#endif

using namespace std;
void raise_error(sql::SQLException e, ostringstream &stream, string func);

class MySQL {
	sql::Connection *con;
	vector<int> _get_sales_periods();
	map<int, SalesPeriod> _get_sales_period_periods()
  public:
	string connect(string, string, string, string);

	// to generate a whole set of sales periods (may require entire reset), to add extra sales periods
	// TODO:
	string regenerate_sales_periods();
	string extend_sales_periods();

	// to clear and generate the customer sales periods
	string clear_csp();
	string generate_csp();

	// to add all the csp's for a new customer, and update their store count for an existing one
	string add_customer_csp(int);
	string update_cust_csp(int);

	// generate the actual sku sales estimates
	string generate_skusales();
};

string MySQL::connect(string db_name, string user, string password, string connection)
{
	ostringstream stream;
	try{
		sql::Driver *driver;

		driver = get_driver_instance();
		con = driver->connect(connection, user, password);
		con->setSchema(db_name);
		stream << "Successfully connected to " << connection << " > " << db_name;
	} catch (sql::SQLException &e) {
		raise_error(e, stream, __FUNCTION__);
	}
	return stream.str();
}

string MySQL::clear_csp()
{
	ostringstream stream;
	try
	{
		sql::Statement *stmt;
		sql::ResultSet *res;

		stmt = con->createStatement();
		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;");
		res->next();
		stream << "Deleting " << res->getInt(1) << " Customer Sales Period Records";
		stmt->execute("DELETE FROM SalesEstimates_customersalesperiod;");
	} catch (sql::SQLException &e) {
		raise_error(e, stream, __FUNCTION__);
	}
	return stream.str();
}

string MySQL::generate_csp()
{
	ostringstream stream;
	try {
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
	} catch (sql::SQLException &e) {
		raise_error(e, stream, __FUNCTION__);
	}
	return stream.str();
}

string MySQL::add_customer_csp(int cust_id)
{
	ostringstream stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		stmt = con->createStatement();
		vector<int> sales_periods = _get_sales_periods();

		ostringstream q_stream1;
		q_stream1 << "SELECT name, dft_store_count FROM SalesEstimates_customer WHERE id=";
		q_stream1 << cust_id << ";";
		string query = q_stream1.str();
		res = stmt->executeQuery(query); res->next();
		string name = res->getString("name");
		int store_count = res->getInt("dft_store_count");
		stream << "Generating CSP for  '" << name << "' with store count: " << store_count << endl;
		ostringstream query_stream;
		query_stream << "INSERT INTO SalesEstimates_customersalesperiod(customer_id, period_id, store_count) VALUES";
		bool first_set = true;
		int add_count = 0;
		for(vector<int>::iterator pid = sales_periods.begin(); pid != sales_periods.end(); ++pid)
		{
			if (!first_set)
				query_stream << ",";
			first_set = false;
			query_stream << "(" << cust_id << "," << *pid << "," << store_count << ")";
			add_count++;
		}
		query_stream << ";";
		query = query_stream.str();
		stmt->execute(query);
		stream << "Added " << add_count << " Customer Sales Period Records";
		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, stream, __FUNCTION__);
	}
	return stream.str();
}

string MySQL::update_cust_csp(int cust_id)
{
	ostringstream stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		stmt = con->createStatement();
		vector<int> sales_periods = _get_sales_periods();

		ostringstream q_stream1;
		q_stream1 << "SELECT name, dft_store_count FROM SalesEstimates_customer WHERE id=";
		q_stream1 << cust_id << ";";
		string query = q_stream1.str();
		res = stmt->executeQuery(query); res->next();
		string name = res->getString("name");
		int store_count = res->getInt("dft_store_count");
		stream << "Updating  '" << name << "' with store count: " << store_count << endl;
		ostringstream query_stream;
		query_stream << "UPDATE SalesEstimates_customersalesperiod SET store_count=" << store_count;
		query_stream << " WHERE customer_id=" << cust_id << " && custom_store_count=False;";
		query = query_stream.str();
		stmt->execute(query);
		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, stream, __FUNCTION__);
	}
	return stream.str();
}

typedef pair<struct tm, struct tm> SalesPeriod;

string MySQL::generate_skusales()
{
	ostringstream stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		sql::ResultSet *res2;
		sql::ResultSet *res3;
		stmt = con->createStatement();


		stmt = con->createStatement();
		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_skusales;");res->next();
		stream << "Deleting " << res->getInt(1) << " SKU Sales Estimates" << endl;
		stmt->execute("TRUNCATE SalesEstimates_skusales;");

		map<int, SalesPeriod> sales_periods = _get_sales_period_periods();

		res = stmt->executeQuery("SELECT id, customer_id, period_id, store_count FROM SalesEstimates_customersalesperiod;");
		ostringstream query_stream;
		query_stream << "INSERT INTO SalesEstimates_skusales(period_id, csku_id, sales, income) VALUES";
		bool first_set = true;
		int start_month;
		double seasonal_srf, sales, store_count, cskui_srf, cskui_price, income;
		SalesPeriod period;
		int add_count = 0;
		while (res->next()) {
			period = sales_periods[res->getInt("period_id")];
			store_count = (double)res->getInt("store_count");
			start_month = period.first.tm_mon + 1;
			ostringstream query_cskui;
			query_cskui << "SELECT id, season_var_id, srf, price FROM SalesEstimates_customerskuinfo WHERE customer_id=" << res->getInt("customer_id") << ";";
			res2 = stmt->executeQuery(query_cskui.str());
			while (res2->next()) {
				if (!first_set)
					query_stream << ",";
				first_set = false;
				ostringstream month_q;
				month_q << "SELECT srf FROM SalesEstimates_monthvariation WHERE season_var_id=" << res2->getInt("season_var_id");
				month_q << " && month=" << start_month << ";";
				seasonal_srf = 1;
				res3 = stmt->executeQuery(month_q.str());
				if (res3->next())
				{
					seasonal_srf = res3->getDouble("srf");
				}
				cskui_srf = res2->getDouble("srf");
				cskui_price = res2->getDouble("price");
				sales = store_count*cskui_srf*seasonal_srf;
				income = sales*cskui_price;
//				stream << "sales: " << sales << ", income: " << income << endl;
				add_count++;
				query_stream << "(" << res->getInt("id") << "," << res2->getInt("id") << "," << sales << "," << income << ")";
			}
		}
		query_stream << ";";
//		stream << "query: " << query_stream.str() << endl;
		stmt->execute(query_stream.str());
		stream << "Added " << add_count << " Customer Sales Period Records";
		res = stmt->executeQuery("SELECT id FROM SalesEstimates_salesperiod;");
		while (res->next()) {
			map<int, double> order_group_costs;
			ostringstream orderg_q;
			orderg_q << "SELECT sales FROM SalesEstimates_skusales" << endl;
			orderg_q << "INNER JOIN"
//SELECT * FROM SalesEstimates_skusales
//LEFT JOIN SalesEstimates_customersalesperiod ON SalesEstimates_skusales.period_id = SalesEstimates_customersalesperiod.id
//LEFT JOIN SalesEstimates_salesperiod ON SalesEstimates_customersalesperiod.period_id = SalesEstimates_salesperiod.id
//LEFT JOIN SalesEstimates_customerskuinfo ON SalesEstimates_skusales.csku_id = SalesEstimates_customerskuinfo.id
//LEFT JOIN SalesEstimates_sku ON SalesEstimates_customerskuinfo.sku_id = SalesEstimates_sku.id
//LEFT JOIN SalesEstimates_sku_assemblies ON SalesEstimates_sku.id = SalesEstimates_sku_assemblies.sku_id
//LEFT JOIN SalesEstimates_assembly ON SalesEstimates_sku_assemblies.assembly_id = SalesEstimates_assembly.id
//LEFT JOIN SalesEstimates_assembly_components ON SalesEstimates_assembly.id = SalesEstimates_assembly_components.assembly_id
//LEFT JOIN SalesEstimates_component ON SalesEstimates_assembly_components.component_id = SalesEstimates_component.id
//LEFT JOIN SalesEstimates_ordergroup ON SalesEstimates_component.order_group_id = SalesEstimates_ordergroup.id
//LEFT JOIN SalesEstimates_costlevel ON SalesEstimates_ordergroup.id = SalesEstimates_costlevel.order_group_id
//GROUP BY SalesEstimates_skusales.id

//SELECT SKUS.id, SKUS.sales, CSP.period_id, OG.id FROM SalesEstimates_skusales SKUS
//LEFT JOIN SalesEstimates_customersalesperiod CSP ON SKUS.period_id = CSP.id
//#LEFT JOIN SalesEstimates_salesperiod ON CSP.period_id = SalesEstimates_salesperiod.id
//LEFT JOIN SalesEstimates_customerskuinfo ON SKUS.csku_id = SalesEstimates_customerskuinfo.id
//LEFT JOIN SalesEstimates_sku ON SalesEstimates_customerskuinfo.sku_id = SalesEstimates_sku.id
//LEFT JOIN SalesEstimates_sku_assemblies ON SalesEstimates_sku.id = SalesEstimates_sku_assemblies.sku_id
//LEFT JOIN SalesEstimates_assembly ON SalesEstimates_sku_assemblies.assembly_id = SalesEstimates_assembly.id
//LEFT JOIN SalesEstimates_assembly_components ON SalesEstimates_assembly.id = SalesEstimates_assembly_components.assembly_id
//LEFT JOIN SalesEstimates_component ON SalesEstimates_assembly_components.component_id = SalesEstimates_component.id
//LEFT JOIN SalesEstimates_ordergroup OG ON SalesEstimates_component.order_group_id = OG.id
//#LEFT JOIN SalesEstimates_costlevel ON SalesEstimates_ordergroup.id = SalesEstimates_costlevel.order_group_id
//GROUP BY SKUS.id
		}
		delete res;
		delete res2;
		delete res3;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, stream, __FUNCTION__);
	}
	return stream.str();
}

map<int, SalesPeriod> MySQL::_get_sales_period_periods()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	map<int, SalesPeriod> sales_periods;
	res = stmt->executeQuery("SELECT id, start_date, finish_date FROM SalesEstimates_salesperiod;");
	struct tm start_tm;
	struct tm finish_tm;
	while (res->next()) {

		memset(&start_tm, 0, sizeof(struct tm));
		memset(&finish_tm, 0, sizeof(struct tm));
		strptime(res->getString(2).c_str(), "%Y-%m-%d %z", &start_tm);
		mktime(&start_tm);
		strptime(res->getString(3).c_str(), "%Y-%m-%d", &finish_tm);
		mktime(&finish_tm);

//			cout << res->getInt("id") << endl;
//			char buf [80];
//			strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M %z", &start_tm);
//			cout << "start_tm: ";
//			puts(buf);
//			strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M %z", &finish_tm);
//			cout << "finish_tm: ";
//			puts(buf);
		sales_periods[res->getInt("id")] = SalesPeriod(start_tm,  finish_tm);
	}
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

void raise_error(sql::SQLException e, ostringstream &stream, string func)
{
	stream << "# ERR: SQLException in " << __FILE__ << ", function: " << func << endl;
	stream << "# ERR: " << e.what();
	stream << " (MySQL error code: " << e.getErrorCode();
	stream << ", SQLState: " << e.getSQLState() << " )";
#ifdef PYTHON
    PyErr_SetString(PyExc_RuntimeError, stream.str().c_str());
    throw_error_already_set();
#endif
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

BOOST_PYTHON_MODULE(worker)
{
    class_<MySQL>("MySQL")
        .def("connect", &MySQL::connect)
        .def("generate_csp", &MySQL::generate_csp)
        .def("clear_csp", &MySQL::clear_csp)
        .def("add_customer_csp", &MySQL::add_customer_csp)
        .def("update_cust_csp", &MySQL::update_cust_csp)
        .def("generate_skusales", &MySQL::generate_skusales)
    ;
}
#else

int main(int, char*[])
{
	connect();
}
#endif
