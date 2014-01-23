#include "worker.h"

void ComponentOrderGroup::add_group(int quantity, double price){
	order_levels.push_back(quantity);
	cost_levels.push_back(price);
}

void ComponentOrderGroup::print(){
	for (unsigned int j = 0; j < order_levels.size(); j++)
		cout << "order_level: " << order_levels[j] << ", cost_levels: " << cost_levels[j] << endl;
}

float ComponentOrderGroup::get_price(int quantity){
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

map<int, Promotion> MySQL::_get_promotions()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	map<int, Promotion> promotions;
	ostringstream query_stream;
	query_stream << "SELECT PROM.id p_id, PROM.srf srf, PROM.price_ratio price_ratio, SKU.id sku_id FROM SalesEstimates_sku SKU" << endl;
	query_stream << "JOIN SalesEstimates_promotion_skus ON SKU.id = SalesEstimates_promotion_skus.sku_id" << endl;
	query_stream << "JOIN SalesEstimates_promotion PROM ON SalesEstimates_promotion_skus.promotion_id = PROM.id" << endl;
	query_stream << "ORDER BY p_id";
	res = stmt->executeQuery(query_stream.str());

	int p_id;
	int old_p_id = -1;
	while (res->next()) {
		p_id = res->getInt("p_id");
		if (old_p_id != p_id){
			promotions[p_id] = {(double)res->getDouble("srf"), (double)res->getDouble("price_ratio"), {res->getInt("sku_id")}};
		} else{
			promotions[p_id].skus.push_back(res->getInt("sku_id"));
		}
		old_p_id = p_id;
	}
	delete res;

//	for (map<int, Promotion>::iterator iter = promotions.begin(); iter != promotions.end(); ++iter) {
//		cout << "promotion: " << iter->first << ": srf: " << iter->second.srf << ", price_ratio: " << iter->second.price_ratio << endl;
//		cout << "   sku: ";
//		for(vector<int>::iterator iter2 = iter->second.skus.begin(); iter2 != iter->second.skus.end(); ++iter2) {
//			cout << *iter2 << ", ";
//		}
//		cout << endl;
//	}
	return promotions;
}

map<int, vector<CSKUI>> MySQL::_get_cskuis()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	map<int, vector<CSKUI>> cskui_customer;
	res = stmt->executeQuery("SELECT customer_id, id, sku_id, season_var_id, srf, price FROM SalesEstimates_customerskuinfo ORDER BY customer_id");
	while (res->next()) {
		cskui_customer[res->getInt("customer_id")].push_back({
			res->getInt("id"),
			res->getInt("sku_id"),
			res->getInt("season_var_id"),
			(double)res->getDouble("srf"),
			(double)res->getDouble("price")
		});
	}
	delete res;
	return cskui_customer;
}

map<IntInt, double> MySQL::_get_seasonal_vars()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	map<IntInt, double> seasonal_vars;
	res = stmt->executeQuery("SELECT season_var_id, month, srf FROM SalesEstimates_monthvariation");
	IntInt seasonal_var;
	while (res->next()) {
		seasonal_var = IntInt(res->getInt("season_var_id"), res->getInt("month"));
		seasonal_vars[seasonal_var] = res->getDouble("srf");
	}
	delete res;
	return seasonal_vars;
}

map<int, ComponentOrderGroup> MySQL::_get_order_group_costs()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();

	ostringstream query_stream;
	query_stream << "SELECT CL.order_group_id, CL.order_quantity, CL.price, OG.minimum_order FROM SalesEstimates_costlevel CL" << endl;
	query_stream << "LEFT JOIN SalesEstimates_ordergroup OG ON CL.order_group_id = OG.id" << endl;
	query_stream << "ORDER BY order_group_id, order_quantity";
	res = stmt->executeQuery(query_stream.str());
	ComponentOrderGroup order_group;
	int old_og_id = -1;
	map<int, ComponentOrderGroup> order_group_costs;
	while (res->next()) {
		if (old_og_id != res->getInt("order_group_id") && old_og_id != -1){
			order_group_costs[old_og_id] = order_group;
			order_group = ComponentOrderGroup();
		}
		order_group.add_group(res->getInt("order_quantity"), res->getDouble("price"));
		order_group.minimum_order = res->getInt("minimum_order");
		old_og_id = res->getInt("order_group_id");
	}
	order_group_costs[old_og_id] = order_group;
	delete res;
	return order_group_costs;
}

map<int, SalesPeriod> MySQL::_get_sales_period_dates()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	map<int, SalesPeriod> sales_periods;
	res = stmt->executeQuery("SELECT id, start_date, finish_date FROM SalesEstimates_salesperiod ORDER BY start_date");
	struct tm start_tm;
	struct tm finish_tm;
	while (res->next()) {
		memset(&start_tm, 0, sizeof(struct tm));
		memset(&finish_tm, 0, sizeof(struct tm));
		strptime(res->getString("start_date").c_str(), "%Y-%m-%d", &start_tm);
		mktime(&start_tm);
		strptime(res->getString("finish_date").c_str(), "%Y-%m-%d", &finish_tm);
		mktime(&finish_tm);
//		cout << res->getInt("id") << ", start: "<< res->getString("start_date") << ", finish: "<< res->getString("finish_date") << endl;
//		char buf [80];
//		strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M %z", &start_tm);
//		cout << "start_tm: ";
//		puts(buf);
//		strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M %z", &finish_tm);
//		cout << "finish_tm: ";
//		puts(buf);
		sales_periods[res->getInt("id")] = SalesPeriod(start_tm,  finish_tm);
	}
	delete res;
	return sales_periods;
}

string MySQL::_construct_demand(map<int, int> og_sales, int start_p, int end_p, int &add_count)
{
	cout << "Demand Period start: " << date_string(sales_periods[start_p].first) << endl;
//	cout << "Demand Period end: " << date_string(sales_periods[end_p].second) << endl;

	ostringstream query_stream;
	bool first_set = true;
	for (map<int, int>::iterator iter = og_sales.begin(); iter != og_sales.end(); ++iter) {
		if (!first_set)
			query_stream << ",";
		first_set = false;
		query_stream << "(" << start_p << "," << end_p << "," << iter->first << ","  << iter->second << ")";
		add_count++;
	}
	return query_stream.str();
}

string MySQL::_construct_order(int items, int start_period_id, int og_id, vector<int> demand_ids, int &add_count, bool &first_set)
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	double cost = order_group_costs[og_id].get_price(items) * (double)items;
	struct tm start_date = sales_periods[start_period_id].first;
	string date_str = mysql_date_string(start_date);
	ostringstream query_stream;
	query_stream << "INSERT INTO SalesEstimates_order(place_date, order_group_id, items, cost) VALUES";
	query_stream << "('" << date_str << "'," << og_id << "," << items << "," << cost << ")" << endl;
	stmt->execute(query_stream.str());
	query_stream.str("");
	query_stream.clear();
	query_stream << "SELECT LAST_INSERT_ID()";
	res = stmt->executeQuery(query_stream.str()); res->next();
	int order_id = res->getInt(1);
	add_count++;
	delete res;
	delete stmt;
	query_stream.str("");
	query_stream.clear();
	for(vector<int>::iterator iter = demand_ids.begin(); iter != demand_ids.end(); ++iter) {
		if (!first_set)
			query_stream << ",";
		first_set = false;
		query_stream << "(" << *iter << "," << order_id << ")";
	}
	return query_stream.str();
}

vector<int> MySQL::_get_order_groups()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	vector<int> order_groups;
	res = stmt->executeQuery("SELECT id FROM SalesEstimates_ordergroup");
	while (res->next()) {
		order_groups.push_back(res->getInt("id"));
	}
	return order_groups;
}

vector<int> MySQL::_get_sales_periods()
{
	sql::Statement *stmt;
	sql::ResultSet *res;
	stmt = con->createStatement();
	vector<int> sales_periods;
	res = stmt->executeQuery("SELECT id FROM SalesEstimates_salesperiod");
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

string date_string(struct tm start_tm){
	char buf [200];
	strftime(buf, sizeof(buf), "%a %d-%m-%Y", &start_tm);//%H:%M %z
	return string(buf);
}

string mysql_date_string(struct tm start_tm){
	char buf [200];
	strftime(buf, sizeof(buf), "%Y-%m-%d", &start_tm);//%H:%M %z
	return string(buf);
}



