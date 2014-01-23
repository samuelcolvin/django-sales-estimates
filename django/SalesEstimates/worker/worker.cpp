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

string MySQL::calculate_demand(int combined_periods)
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
		query_stream << "INSERT INTO SalesEstimates_demand(start_period_id, end_period_id, order_group_id, items) VALUES" << endl;
//		order_group_costs = _get_order_group_costs();
		vector<int> order_groups = _get_order_groups();
		sales_periods = _get_sales_period_dates();
		int index = 1;
		int start_index = 1;
		int start_sales_period = 0;
		int sales_period = 0;
		map<int, int> og_sales;
		map<int, int>::iterator int_int_it;
		bool first_set = true;
		int add_count = 0;
		for (map<int, SalesPeriod>::iterator iter = sales_periods.begin(); iter != sales_periods.end(); ++iter) {
			if (index == start_index){
				start_sales_period = iter->first;
			}
			sales_period = iter->first;
			if (index - start_index == combined_periods - 1){
				start_index = index + 1;
				if (!first_set)
					query_stream << ",";
				first_set = false;
				query_stream << _construct_demand(og_sales, start_sales_period, sales_period, add_count);
				og_sales.clear();
			}
			for(vector<int>::iterator iter2 = order_groups.begin(); iter2 != order_groups.end(); ++iter2) {
				iorder = IntInt(iter->first, *iter2);
				it = og_total_sales.find(iorder);
				if(it != og_total_sales.end())
				{
					prev_sales = 0;
					int_int_it = og_sales.find(*iter2);
					if(int_int_it != og_sales.end())
					{ prev_sales = int_int_it->second; }
					og_sales[*iter2] = prev_sales + it->second;
				}
			}
			index++;
		}
		query_stream << "," << _construct_demand(og_sales, start_sales_period, sales_period, add_count);
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
//		vector<int> order_groups = _get_order_groups();
		sales_periods = _get_sales_period_dates();
		ostringstream query_stream;
		query_stream << "SELECT D.id, D.start_period_id, D.order_group_id, D.items FROM SalesEstimates_demand D" << endl;
		query_stream << "LEFT JOIN SalesEstimates_salesperiod SP ON D.start_period_id = SP.id" << endl;
		query_stream << "ORDER BY D.order_group_id, SP.start_date" << endl;
		res = stmt->executeQuery(query_stream.str());

		query_stream.str("");
		query_stream.clear();
		query_stream << "INSERT INTO SalesEstimates_demand(id, order_id) VALUES" << endl;
		bool first_set = true;

		int add_count = 0;
		int og_id, items, min_order;
		int start_period_id = -1;
		int current_period_id = -1;
		bool res_next = res->next();
		vector<int> demand_ids;
		while (res_next) {
			og_id = res->getInt("order_group_id");
			min_order = order_group_costs[og_id].minimum_order;
			items = 0;
			demand_ids.clear();
			while (og_id == res->getInt("order_group_id")) {
				current_period_id = res->getInt("start_period_id");
				if (items == 0)
					start_period_id = current_period_id;
				items += res->getInt("items");
				demand_ids.push_back(res->getInt("id"));
				res_next = res->next();
				if (!res_next)
					break;
				if (items >= min_order && current_period_id != res->getInt("start_period_id")){
					query_stream << _construct_order(items, start_period_id, og_id, demand_ids, add_count, first_set);
					demand_ids.clear();
					items = 0;
				}
			}
			if (items > 0)
				query_stream << _construct_order(items, start_period_id, og_id, demand_ids, add_count, first_set);
		}
		query_stream << endl << "ON DUPLICATE KEY UPDATE order_id=VALUES(order_id)";
		stmt->execute(query_stream.str());
		out_stream << "Added " << add_count << " Demands";
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
        .def("calculate_demand", &MySQL::calculate_demand)
        .def("generate_orders", &MySQL::generate_orders)
    ;
}
#else

int main(int, char*[])
{
	//not working - would need some work it this file were to be tested outside python
	connect();
}
#endif
