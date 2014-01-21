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
void print_columns(sql::ResultSet *rs);

typedef pair<struct tm, struct tm> SalesPeriod;
typedef pair<int, int> IntInt;

class MySQL {
	sql::Connection *con;
	vector<int> _get_sales_periods();
	map<int, SalesPeriod> _get_sales_period_periods();
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
		stream << "Successfully connected to " << connection << " > " << db_name << endl;
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
		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_skusales;");
		res->next();
		stream << "Deleting " << res->getInt(1) << " SKU Sales Records" << endl;
		stmt->execute("DELETE FROM SalesEstimates_skusales;");

		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;");
		res->next();
		stream << "Deleting " << res->getInt(1) << " Customer Sales Period Records" << endl;
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
		stream << "Added " << add_count << " Customer Sales Period Records" << endl;

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
		stream << "Added " << add_count << " Customer Sales Period Records" << endl;
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

class OrderGroup {
	vector<int> order_levels;
	vector<double> cost_levels;
  public:
	void add_group(int quantity, double price){
		order_levels.push_back(quantity);
		cost_levels.push_back(price);
	}

	void print(){
		for (unsigned int j = 0; j < order_levels.size(); j++)
			cout << "order_level: " << order_levels[j] << ", cost_levels: " << cost_levels[j] << endl;
	}

	float get_price(int quantity){
		double price = 0;
		if (order_levels.size() != 0){
			price = cost_levels[0];
			for (unsigned int i = 0; i < order_levels.size(); i++) {
			  if (order_levels[i] > quantity)
				  break;
			  price = cost_levels[i];
			}
		}
//		cout << "quantity: " << quantity << ", price: " << price << endl;
//		print();
		return price;
	}
};

struct SKUSalesInfo {
	int period_id;
	int sales;
	vector<IntInt> og__count;
};

string MySQL::generate_skusales()
{
	ostringstream stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		sql::ResultSet *res2;
		sql::ResultSet *res3;
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
//		stream << "query: " << query_stream.str() << endl;
		stmt->execute(query_stream.str());
		stream << "Added " << add_count << " Customer Sales Period Records";

		query_stream.str("");
		query_stream.clear();
		query_stream << "SELECT SKUS.id sku_sales_id, SKUS.sales sales, CSP.period_id period_id, OG.id og_id, AC.count c_count FROM SalesEstimates_skusales SKUS" << endl;
		query_stream << "LEFT JOIN SalesEstimates_customersalesperiod CSP ON SKUS.period_id = CSP.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_customerskuinfo ON SKUS.csku_id = SalesEstimates_customerskuinfo.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_sku ON SalesEstimates_customerskuinfo.sku_id = SalesEstimates_sku.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_sku_assemblies ON SalesEstimates_sku.id = SalesEstimates_sku_assemblies.sku_id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_assembly ON SalesEstimates_sku_assemblies.assembly_id = SalesEstimates_assembly.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_assycomponent AC ON SalesEstimates_assembly.id = AC.assembly_id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_component ON AC.component_id = SalesEstimates_component.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_ordergroup OG ON SalesEstimates_component.order_group_id = OG.id" << endl;
		query_stream << "ORDER BY sku_sales_id";
		res = stmt->executeQuery(query_stream.str());

		map<IntInt, int> og_total_sales;
		map<IntInt, int>::iterator it;
		IntInt iorder;
		int prev_sales, sk_sales_id;

		map<int, SKUSalesInfo> sku_sales_infos;
		map<int, SKUSalesInfo>::iterator it_skusa;

		while (res->next()) {
			iorder = IntInt(res->getInt("period_id"), res->getInt("og_id"));
			prev_sales = 0;
			it = og_total_sales.find(iorder);
			if(it != og_total_sales.end())
			{ prev_sales = it->second; }
			og_total_sales[iorder] = prev_sales + res->getInt("sales") * res->getInt("c_count");
			sk_sales_id = res->getInt("sku_sales_id");
			it_skusa = sku_sales_infos.find(sk_sales_id);
			if (it_skusa == sku_sales_infos.end()){
				sku_sales_infos[sk_sales_id] = {res->getInt("period_id"), res->getInt("sales"), {IntInt(res->getInt("og_id"), res->getInt("c_count"))}};
			} else{
				it_skusa->second.og__count.push_back(IntInt(res->getInt("og_id"), res->getInt("c_count")));
			}
		}
		query_stream.str("");
		query_stream.clear();
		query_stream << "SELECT order_group_id, order_quantity, price FROM SalesEstimates_costlevel" << endl;
		query_stream << "ORDER BY order_group_id, order_quantity";
		res = stmt->executeQuery(query_stream.str());
		OrderGroup order_group;
		int old_og_id = -1;
		map<int, OrderGroup> order_group_calcs;
		while (res->next()) {
			if (old_og_id != res->getInt("order_group_id") && old_og_id != -1){
				order_group_calcs[old_og_id] = order_group;
				order_group = OrderGroup();
			}
			order_group.add_group(res->getInt("order_quantity"), res->getDouble("price"));
			old_og_id = res->getInt("order_group_id");
		}
		order_group_calcs[old_og_id] = order_group;

		map<IntInt, double> order_prices;
		for (it = og_total_sales.begin(); it != og_total_sales.end(); ++it) {
			order_prices[it->first] = order_group_calcs[it->first.second].get_price(it->second);
		}

		query_stream.str("");
		query_stream.clear();
		query_stream << "INSERT INTO SalesEstimates_skusales(id, cost) VALUES";
		first_set = true;
		double cost;
		for(map<int, SKUSalesInfo>::iterator skui_it = sku_sales_infos.begin(); skui_it != sku_sales_infos.end(); skui_it++) {
			if (!first_set)
				query_stream << ",";
			first_set = false;
			cost = 0;

			for(vector<IntInt>::iterator it2 = skui_it->second.og__count.begin(); it2 != skui_it->second.og__count.end(); it2++) {
			    iorder = IntInt(skui_it->second.period_id, it2->first);
			    cost += order_prices[iorder] * it2->second;
			}
			cost *= skui_it->second.sales;
			query_stream << "(" << skui_it->first << "," << cost << ")";
		}
		query_stream << endl << "ON DUPLICATE KEY UPDATE cost=VALUES(cost);";
		stmt->execute(query_stream.str());
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
	return sales_periods;
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

void print_columns(sql::ResultSet *rs)
{
	sql::ResultSetMetaData *res_meta;
	res_meta = rs -> getMetaData();
	int numcols = res_meta -> getColumnCount();
	cout << "\nNumber of columns in the result set = " << numcols << endl;
	cout.width(20);
	cout << "Column Name/Label";
	cout.width(20);
	cout << "Column Type";
	cout.width(20);
	cout << "Column Size" << endl;
	for (int i = 0; i < numcols; ++i) {
	  cout.width(20);
	  cout << res_meta -> getColumnLabel (i+1);
	  cout.width(20);
	  cout << res_meta -> getColumnTypeName (i+1);
	  cout.width(20);
	  cout << res_meta -> getColumnDisplaySize (i+1) << endl;
	}
	cout << "\nColumn \"" << res_meta -> getColumnLabel(1);
	cout << "\" belongs to the Table: \"" << res_meta -> getTableName(1);
	cout << "\" which belongs to the Schema: \"" << res_meta -> getSchemaName(1) << "\"" << endl;
}

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
	//not working - would need some work it this file were to be tested outside python
	connect();
}
#endif
