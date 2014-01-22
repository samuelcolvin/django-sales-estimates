#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <vector>
#include <time.h>

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

struct CSKUI {
	int id;
	int sku_id;
	int season_var_id;
	double srf;
	double price;
};

struct Promotion {
	double srf;
	double price_ratio;
	vector<int> skus;
};

struct SKUSalesInfo {
	int period_id;
	int sales;
	vector<IntInt> og__count;
};

class ComponentOrderGroup {
	vector<int> order_levels;
	vector<double> cost_levels;
  public:
	void add_group(int, double);

	void print();

	float get_price(int);
};

class MySQL {
	sql::Connection *con;
	vector<int> _get_sales_periods();
	map<int, SalesPeriod> _get_sales_period_dates();
	map<IntInt, double> _get_seasonal_vars();
	map<int, vector<CSKUI>> _get_cskuis();
	map<int, Promotion> _get_promotions();
	map<int, OrderGroup> _get_order_prices();
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

	// calculate the supply demand associated with sku sales
	string calculate_demand(int);
};
