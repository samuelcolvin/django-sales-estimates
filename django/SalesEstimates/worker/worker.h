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
void raise_error(sql::SQLException, ostringstream&, string);
void print_columns(sql::ResultSet*);
string date_string(struct tm);
string mysql_date_string(struct tm);
time_t date_t(struct tm);
time_t date_from_mysql(string, struct tm*);
struct tm date_tm(time_t);
time_t sub_days(struct tm, int);

typedef pair<struct tm, struct tm> SalesPeriod;
typedef pair<int, int> IntInt;
struct DblTimet {
	double items;
	time_t order_date;
	int lead_time;
};

struct CSKUI {
	int id;
	int sku_id;
	int season_var_id;
	double srf;
	double price;
};

struct OGSPDemand {
	double items;
	int cust_lt;
	int assy_lt;
	int comp_lt;
};

struct Promotion {
	double srf;
	double price_ratio;
	vector<int> skus;
};

class ComponentOrderGroup {
	vector<int> order_levels;
	vector<double> cost_levels;
  public:
	int minimum_order;
	void add_group(int, double);

	void print();

	float get_price(int);
};

class MySQL {
	sql::Connection *con;
	map<int, ComponentOrderGroup> order_group_costs;
	map<int, SalesPeriod> sales_periods;
	vector<int> _get_sales_periods();
	map<int, SalesPeriod> _get_sales_period_dates();
	map<IntInt, double> _get_seasonal_vars();
	map<int, vector<CSKUI>> _get_cskuis();
	map<int, Promotion> _get_promotions();
	map<int, ComponentOrderGroup> _get_order_group_costs();
	vector<int> _get_order_groups();
	string _construct_demand(map<int, DblTimet>, int, int, int&);
	string _construct_order(int, time_t, int, int, vector<int>, int&, bool&);
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

	// calculate the demand associated with sku sales
	string calculate_demand(int, int);

	// generate orders to satisfy demand
	string generate_orders();

	// function for testing things out
	string test_date_arith();
};
