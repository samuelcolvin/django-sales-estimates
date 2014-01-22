#include "worker.h"

string MySQL::connect(string db_name, string user, string password, string connection)
{
	ostringstream out_stream;
	try{
		sql::Driver *driver;

		driver = get_driver_instance();
		con = driver->connect(connection, user, password);
		con->setSchema(db_name);
		out_stream << "Successfully connected to " << connection << " > " << db_name << endl;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::clear_csp()
{
	ostringstream out_stream;
	try
	{
		sql::Statement *stmt;
		sql::ResultSet *res;

		stmt = con->createStatement();
		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_skusales;");
		res->next();
		out_stream << "Deleting " << res->getInt(1) << " SKU Sales Records" << endl;
		stmt->execute("DELETE FROM SalesEstimates_skusales;");

		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;");
		res->next();
		out_stream << "Deleting " << res->getInt(1) << " Customer Sales Period Records" << endl;
		stmt->execute("DELETE FROM SalesEstimates_customersalesperiod;");
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::generate_csp()
{
	ostringstream out_stream;
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
		out_stream << "Added " << add_count << " Customer Sales Period Records" << endl;

		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::add_customer_csp(int cust_id)
{
	ostringstream out_stream;
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
		out_stream << "Generating CSP for  '" << name << "' with store count: " << store_count << endl;
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
		out_stream << "Added " << add_count << " Customer Sales Period Records" << endl;
		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::update_cust_csp(int cust_id)
{
	ostringstream out_stream;
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
		out_stream << "Updating  '" << name << "' with store count: " << store_count << endl;
		ostringstream query_stream;
		query_stream << "UPDATE SalesEstimates_customersalesperiod SET store_count=" << store_count;
		query_stream << " WHERE customer_id=" << cust_id << " && custom_store_count=False;";
		query = query_stream.str();
		stmt->execute(query);
		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::generate_skusales()
{
	ostringstream out_stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		stmt = con->createStatement();

		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_skusales;");res->next();
		out_stream << "Deleting " << res->getInt(1) << " SKU Sales Estimates" << endl;
		stmt->execute("TRUNCATE SalesEstimates_skusales;");

		map<int, SalesPeriod> sales_periods = _get_sales_period_dates();
		map<IntInt, double> seasonal_vars = _get_seasonal_vars();
		map<IntInt, double>::iterator it_db;

		map<int, vector<CSKUI>> cskuis_customer = _get_cskuis();
		vector<CSKUI> cskuis;
		vector<CSKUI>::iterator it_cskui;

		map<int, Promotion> promotions = _get_promotions();
		Promotion promotion;

		res = stmt->executeQuery("SELECT id, customer_id, period_id, store_count, promotion_id FROM SalesEstimates_customersalesperiod");
		ostringstream query_stream;
		query_stream << "INSERT INTO SalesEstimates_skusales(period_id, csku_id, sales, income) VALUES";
		bool first_set = true;
		int start_month;
		double seasonal_srf, sales, store_count, income, prom_srf, prom_price_ratio;
		SalesPeriod period;
		bool has_prom = false;
		int add_count = 0;
		while (res->next()) {
			period = sales_periods[res->getInt("period_id")];
			store_count = (double)res->getInt("store_count");
			start_month = period.first.tm_mon + 1;

			cskuis = cskuis_customer[res->getInt("customer_id")];
			has_prom = res->getInt("promotion_id") != 0;
			if (has_prom){
				promotion = promotions[res->getInt("promotion_id")];
			}
			for(it_cskui = cskuis.begin(); it_cskui != cskuis.end(); ++it_cskui) {
				if (!first_set)
					query_stream << ",";
				first_set = false;

				it_db = seasonal_vars.find(IntInt(it_cskui->season_var_id, start_month));
				seasonal_srf = it_db != seasonal_vars.end() ? it_db->second : 1;

				prom_srf = 1;
				prom_price_ratio = 1;
				if (has_prom){
					if(find(promotion.skus.begin(), promotion.skus.end(), it_cskui->sku_id) != promotion.skus.end()){
						prom_srf = promotion.srf;
						prom_price_ratio = promotion.price_ratio;
					}
				}

				sales = store_count * it_cskui->srf * seasonal_srf * prom_srf;
				income = sales * it_cskui->price * prom_price_ratio;
//				out_stream << "sales: " << sales << ", income: " << income << endl;
				add_count++;
				query_stream << "(" << res->getInt("id") << "," << it_cskui->id << "," << sales << "," << income << ")";
			}
		}
//		out_stream << "query: " << query_stream.str() << endl;
		stmt->execute(query_stream.str());
		out_stream << "Added " << add_count << " Customer Sales Period Records";

		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

class OrderCollection {
	// TODO: got to here
	vector<int> order_levels;
	vector<double> cost_levels;
  public:
	void add_group(int, double);

	void print();

	float get_price(int);
};

string MySQL::calculate_demand(int combined_periods)
{
	ostringstream out_stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		stmt = con->createStatement();

		ostringstream query_stream;
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
		map<int, ComponentOrderGroup>order_group_calcs = _get_order_prices();

		map<IntInt, double> order_prices;
		for (it = og_total_sales.begin(); it != og_total_sales.end(); ++it) {
			order_prices[it->first] = order_group_calcs[it->first.second].get_price(it->second);
		}

		map<int, SalesPeriod> sales_periods = _get_sales_period_dates();
		int period_number = 1;
		int start_period = 0;
		for (map<int, SalesPeriod>::iterator iter = sales_periods.begin(); iter != sales_periods.end(); ++iter) {
			if (period_number - start_period == combined_periods){
				// finish orders
				start_period = period_number + 1;
			}
			// TODO: got to here
			period_number++;
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
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
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
