#include "worker.h"

string MySQL::connect(string db_name, string user, string password, string connection)
{
	ostringstream out_stream;
	try{
		sql::Driver *driver;

		driver = get_driver_instance();
		con = driver->connect(connection, user, password);
		con->setSchema(db_name);
		out_stream << "Successfully connected to " << connection << ":" << db_name << endl;
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
		stmt->execute("DELETE FROM SalesEstimates_skusales");
		stmt->execute("ALTER TABLE SalesEstimates_skusales AUTO_INCREMENT = 1");

		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_customersalesperiod;");
		res->next();
		out_stream << "Deleting " << res->getInt(1) << " Customer Sales Period Records" << endl;
		stmt->execute("DELETE FROM SalesEstimates_customersalesperiod");
		stmt->execute("ALTER TABLE SalesEstimates_customersalesperiod AUTO_INCREMENT = 1");

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

		sales_periods = _get_sales_period_dates();
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

string MySQL::calculate_demand(int combined_periods, int general_lead_time)
{
	ostringstream out_stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		stmt = con->createStatement();

		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_demand;");res->next();
		out_stream << "Deleting " << res->getInt(1) << " Demands" << endl;
		stmt->execute("TRUNCATE SalesEstimates_demand;");

		ostringstream query_stream;
		query_stream << "SELECT SKUS.id sku_sales_id, SKUS.sales sales, CSP.period_id period_id, OG.id og_id, AC.count c_count, ";
		query_stream << "CUST.delivery_lead_time cust_lt, ASSY.assembly_lead_time assy_lt, COMP.supply_lead_time comp_lt ";
		query_stream << "FROM SalesEstimates_skusales SKUS" << endl;
		query_stream << "LEFT JOIN SalesEstimates_customersalesperiod CSP ON SKUS.period_id = CSP.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_customer CUST ON CSP.customer_id = CUST.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_customerskuinfo ON SKUS.csku_id = SalesEstimates_customerskuinfo.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_sku ON SalesEstimates_customerskuinfo.sku_id = SalesEstimates_sku.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_sku_assemblies ON SalesEstimates_sku.id = SalesEstimates_sku_assemblies.sku_id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_assembly ASSY ON SalesEstimates_sku_assemblies.assembly_id = ASSY.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_assycomponent AC ON ASSY.id = AC.assembly_id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_component COMP ON AC.component_id = COMP.id" << endl;
		query_stream << "LEFT JOIN SalesEstimates_ordergroup OG ON COMP.order_group_id = OG.id" << endl;
		query_stream << "ORDER BY sku_sales_id";
//		cout << query_stream.str() << endl;
		res = stmt->executeQuery(query_stream.str());

		// TODO: change second int to a structure/pair containing lead time as well as sales
		map<IntInt, OGSPDemand> og_sp_demand;
		map<IntInt, OGSPDemand>::iterator it_ogspd;
		IntInt iorder;
		double items;
		int cust_lt, assy_lt, comp_lt;

		while (res->next()) {
			iorder = IntInt(res->getInt("period_id"), res->getInt("og_id"));
			items = res->getDouble("sales") * (double)res->getInt("c_count");
			cust_lt = res->getInt("cust_lt");
			assy_lt = res->getInt("assy_lt");
			comp_lt = res->getInt("comp_lt");
			it_ogspd = og_sp_demand.find(iorder);
			if(it_ogspd != og_sp_demand.end())
			{
				it_ogspd->second.items +=  items;
				it_ogspd->second.cust_lt = cust_lt > it_ogspd->second.cust_lt ? cust_lt : it_ogspd->second.cust_lt;
				it_ogspd->second.assy_lt = assy_lt > it_ogspd->second.assy_lt ? assy_lt : it_ogspd->second.assy_lt;
				it_ogspd->second.cust_lt = comp_lt > it_ogspd->second.comp_lt ? comp_lt : it_ogspd->second.comp_lt;
			}
			else{
				og_sp_demand[iorder] = {
					items,
					cust_lt,
					assy_lt,
					comp_lt,
				};
			}
		}
		query_stream.str("");
		query_stream.clear();
		query_stream << "INSERT INTO SalesEstimates_demand(start_period_id, end_period_id, order_group_id, items, required_date, lead_time_total) VALUES" << endl;
		vector<int> order_groups = _get_order_groups();
		sales_periods = _get_sales_period_dates();
		int index = 1;
		int start_index = 1;
		int start_sales_period = 0;
		int sales_period_id = 0;
		map<int, DblTimet> og_items_odate;
		map<int, int> og_component;
		map<int, DblTimet>::iterator int_dbl_t;
		time_t earliest_order_date;
		int lead_days;
		bool first_set = true;
		int add_count = 0;
		for (map<int, SalesPeriod>::iterator it_sp = sales_periods.begin(); it_sp != sales_periods.end(); ++it_sp) {
			sales_period_id = it_sp->first;
			if (index == start_index){
				start_sales_period = sales_period_id;
			}
			for(vector<int>::iterator it_og = order_groups.begin(); it_og != order_groups.end(); ++it_og) {
				iorder = IntInt(sales_period_id, *it_og);
				it_ogspd = og_sp_demand.find(iorder);
				if(it_ogspd != og_sp_demand.end())
				{
					lead_days = general_lead_time + it_ogspd->second.cust_lt + it_ogspd->second.assy_lt + it_ogspd->second.comp_lt;
					earliest_order_date = sub_days(sales_periods[sales_period_id].first, lead_days);
					int_dbl_t = og_items_odate.find(*it_og);
					if(int_dbl_t != og_items_odate.end())
					{
						int_dbl_t->second.items += it_ogspd->second.items;
						if (earliest_order_date < int_dbl_t->second.order_date){
							int_dbl_t->second.order_date = earliest_order_date;
							int_dbl_t->second.lead_time = lead_days;
						}
					} else {
						og_items_odate[*it_og] = {it_ogspd->second.items, earliest_order_date, lead_days};
					}
				}
			}
			if (index - start_index == combined_periods - 1){
				start_index = index + 1;
				if (!first_set)
					query_stream << ",";
				first_set = false;
				query_stream << _construct_demand(og_items_odate, start_sales_period, sales_period_id, add_count);
				og_items_odate.clear();
			}
			index++;
		}
		query_stream << "," << _construct_demand(og_items_odate, start_sales_period, sales_period_id, add_count);
		stmt->execute(query_stream.str());
		out_stream << "Added " << add_count << " Demands";
		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::generate_orders()
{
	ostringstream out_stream;
	try {
		sql::Statement *stmt;
		sql::ResultSet *res;
		stmt = con->createStatement();

		res = stmt->executeQuery("SELECT COUNT(*) FROM SalesEstimates_order");res->next();
		out_stream << "Deleting " << res->getInt(1) << " Orders" << endl;
		stmt->execute("DELETE FROM SalesEstimates_order");
		stmt->execute("ALTER TABLE SalesEstimates_order AUTO_INCREMENT = 1");

		order_group_costs = _get_order_group_costs();
		sales_periods = _get_sales_period_dates();
		ostringstream query_stream;
		query_stream << "SELECT D.id, D.start_period_id, D.order_group_id, D.items, D.required_date FROM SalesEstimates_demand D" << endl;
		query_stream << "LEFT JOIN SalesEstimates_salesperiod SP ON D.start_period_id = SP.id" << endl;
		query_stream << "ORDER BY D.order_group_id, SP.start_date" << endl;
		res = stmt->executeQuery(query_stream.str());

		query_stream.str("");
		query_stream.clear();
		query_stream << "INSERT INTO SalesEstimates_demand(id, order_id) VALUES" << endl;
		bool first_set = true;

		int add_count = 0;
		double items;
		int og_id, min_order;
		int start_period_id = -1;
		int current_period_id = -1;
		bool res_next = res->next();
		time_t earliest_orderdate = 0;
		time_t this_orderdate;
		struct tm datetime;
		vector<int> demand_ids;
		while (res_next) {
			og_id = res->getInt("order_group_id");
			min_order = order_group_costs[og_id].minimum_order;
			items = 0;
			demand_ids.clear();
			while (og_id == res->getInt("order_group_id")) {
				current_period_id = res->getInt("start_period_id");
				if (items == 0){
					start_period_id = current_period_id;
					earliest_orderdate = date_from_mysql(res->getString("required_date"), &datetime);
				} else {
					this_orderdate = date_from_mysql(res->getString("required_date"), &datetime);
					if (this_orderdate < earliest_orderdate)
						earliest_orderdate = this_orderdate;
				}
				items += res->getDouble("items");
				demand_ids.push_back(res->getInt("id"));
				res_next = res->next();
				if (!res_next)
					break;
				if (items >= min_order && current_period_id != res->getInt("start_period_id")){
					query_stream << _construct_order(items, earliest_orderdate, start_period_id, og_id, demand_ids, add_count, first_set);
					demand_ids.clear();
					items = 0;
				}
			}
			if (items > 0)
				query_stream << _construct_order(items, earliest_orderdate, start_period_id, og_id, demand_ids, add_count, first_set);
		}
		query_stream << endl << "ON DUPLICATE KEY UPDATE order_id=VALUES(order_id)";
		stmt->execute(query_stream.str());
		out_stream << "Added " << add_count << " Orders";
		delete res;
		delete stmt;
	} catch (sql::SQLException &e) {
		raise_error(e, out_stream, __FUNCTION__);
	}
	return out_stream.str();
}

string MySQL::test_date_arith()
{
	ostringstream out_stream;
	try {
		sql::Statement *stmt;
		stmt = con->createStatement();
		sales_periods = _get_sales_period_dates();
		time_t tb4 = 0;
		for (map<int, SalesPeriod>::iterator iter = sales_periods.begin(); iter != sales_periods.end(); ++iter) {
			out_stream << "ID: " << iter->first << ", start: " << date_string(iter->second.first);
			time_t startl = date_t(iter->second.first);
			out_stream << ", start long: " << startl << endl;
			struct tm start2 =  date_tm(startl);
			out_stream << "ID: " << iter->first << ", start: " << date_string(start2) << endl;
			time_t t5 = sub_days(iter->second.first, 5);
			struct tm tm5 = date_tm(t5);
			out_stream << "ID: " << iter->first << ", s - 5: " << date_string(tm5) << endl;
			time_t t10 =sub_days(iter->second.first, 10);
			out_stream << "ID: " << iter->first << ", s -10: " << date_string(date_tm(t10)) << endl;
			string resp = t5 < tb4 ? "yes" : "no";
			out_stream << "t - 5  less than tb4: " << resp << endl;
			resp = t10 < tb4 ? "yes" : "no";
			out_stream << "t - 10 less than tb4: " << resp << endl;
			tb4 = startl;
		}
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
        .def("calculate_demand", &MySQL::calculate_demand)
        .def("generate_orders", &MySQL::generate_orders)
        .def("test_date_arith", &MySQL::test_date_arith)
    ;
}
#else

int main(int, char*[])
{
	//not working - would need some work it this file were to be tested outside python
	connect();
}
#endif
