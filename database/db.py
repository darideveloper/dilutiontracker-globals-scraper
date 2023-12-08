import os
from database.mysql import MySQL
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


class Database (MySQL):

    def __init__(self):

        # Connect to mysql
        super().__init__(DB_HOST, DB_NAME, DB_USER, DB_PASS)

        self.premarket_id = None
    
    def save_new_filings(self, new_filings_data: list):
        """ Save in database the new filings data

        Args:
            new_filings_data (list): dicts with rows data
            Structure:
            [
                {
                    "ticker": str,
                    "company_name": str,
                    "dilution_type": str,
                    "dilution_name": str,
                    "date_modified": datetime,
                    "query_date": datetime,
                },
                ...
            ]
        """
        
        for row in new_filings_data:
            
            # Generate insert script
            sql = f""" insert into new_filings (
                        ticker,
                        company_name,
                        dilution_type,
                        dilution_name,
                        date_modified,
                        query_date
                    ) values (
                        {self.get_clean_text(row["ticker"])},
                        {self.get_clean_text(row["company_name"])},
                        {self.get_clean_text(row["dilution_type"])},
                        {self.get_clean_text(row["dilution_name"])},
                        "{row["date_modified"].strftime("%Y-%m-%d")}",
                        "{row["query_date"].strftime("%Y-%m-%d")}"
                    )
            """
            self.run_sql(sql, auto_commit=False)
            
        # Commit changes
        self.commit_close()
    
    def save_completed_offerings(self, completed_offerings_data: list):
        """ Save in database the new completed offerings data

        Args:
            completed_offerings_data (list): dicts with rows data
            Structure:
            [
                {
                    "ticker": str,
                    "type": str,
                    "method": str,
                    "share_equivalent": int,
                    "price": float,
                    "warrants": int,
                    "offering_amt": int,
                    "bank": str,
                    "investors": str,
                    "datetime": datetime,
                    "query_date": datetime,
                },
                ...
            ]
        """
        
        for row in completed_offerings_data:
            
            # Generate insert script
            sql = f"""insert into completed_offerings (
                        ticker,
                        type,
                        method,
                        share_equivalent,
                        price,
                        warrants,
                        offering_amt,
                        bank,
                        investors,
                        datetime,
                        query_date
                    ) values (
                        {self.get_clean_text(row["ticker"])},
                        {self.get_clean_text(row["type"])},
                        {self.get_clean_text(row["method"])},
                        {row["share_equivalent"]},
                        {row["price"]},
                        {row["warrants"]},
                        {row["offering_amt"]},
                        {self.get_clean_text(row["bank"])},
                        {self.get_clean_text(row["investors"])},
                        "{row["datetime"].strftime("%Y-%m-%d %H:%M")}",
                        "{row["query_date"].strftime("%Y-%m-%d")}"
                    )
            """
            self.run_sql(sql, auto_commit=False)
            
        # Commit changes
        self.commit_close()
        
    def save_pending_s1s(self, pending_s1s_data: list):
        """ Save in database the pending s1s data

        Args:
            pending_s1s_data (list): dicts with rows data
            Structure:
            [
                {
                    "ticker": str,
                    "company_name": str,
                    "industry": str,
                    "date_first_s1": datetime,
                    "pricing_date": datetime,
                    "anticipated_deal_size": str,
                    "estimated_warrant_coverage": int,
                    "underwriters_placement_agents": str,
                    "float_before_offering": int,
                    "status": str,
                    "pricing": float,
                    "shares_offered": int,
                    "final_warrant_coverage": int,
                    "exercise_price": float,
                    "query_date": datetime,
                },
                ...
            ]
        """
        
        for row in pending_s1s_data:
        
            # Fix fields
            date_first_s1 = row["date_first_s1"]
            if date_first_s1 != "NULL":
                date_first_s1 = f'"{date_first_s1.strftime("%Y-%m-%d")}"'
            
            pricing_date = row["pricing_date"]
            if pricing_date != "NULL":
                pricing_date = f'"{pricing_date.strftime("%Y-%m-%d")}"'
            
            # Generate insert script
            sql = f"""insert into pending_s1s (
                        ticker,
                        company_name,
                        industry,
                        date_first_s1,
                        pricing_date,
                        anticipated_deal_size,
                        estimated_warrant_coverage,
                        underwriters_placement_agents,
                        float_before_offering,
                        status,
                        pricing,
                        shares_offered,
                        final_warrant_coverage,
                        exercise_price,
                        query_date
                    ) values (
                        {self.get_clean_text(row["ticker"])},
                        {self.get_clean_text(row["company_name"])},
                        {self.get_clean_text(row["industry"])},
                        {date_first_s1},
                        {pricing_date},
                        {self.get_clean_text(row["anticipated_deal_size"])},
                        {row["estimated_warrant_coverage"]},
                        {self.get_clean_text(row["underwriters_placement_agents"])},
                        {row["float_before_offering"]},
                        {self.get_clean_text(row["status"])},
                        {row["pricing"]},
                        {row["shares_offered"]},
                        {row["final_warrant_coverage"]},
                        {row["exercise_price"]},
                        "{row["query_date"].strftime("%Y-%m-%d")}"
                    )
            """
            self.run_sql(sql, auto_commit=False)
            
        # Commit changes
        self.commit_close()
        
    def save_reverse_splits(self, reverse_splits_data: list):
        """ Save in database the reverse splits data

        Args:
            reverse_splits_data (list): dicts with rows data
            Structure:
            [
                {
                    "symbol": str,
                    "effective_date": datetime,
                    "split_ratio": str,
                    "current_float_m": float,
                    "status": str,
                    "query_date": datetime,
                },
                ...
            ]
        """
        
        for row in reverse_splits_data:
        
            # Fix fields
            effective_date = row["effective_date"]
            if effective_date != "NULL":
                effective_date = f'"{effective_date.strftime("%Y-%m-%d")}"'
            
            # Generate insert script
            sql = f"""insert into reverse_splits (
                        symbol,
                        effective_date,
                        split_ratio,
                        current_float_m,
                        status,
                        query_date
                    ) values (
                        {self.get_clean_text(row["symbol"])},
                        {effective_date},
                        {self.get_clean_text(row["split_ratio"])},
                        {row["current_float_m"]},
                        {self.get_clean_text(row["status"])},
                        "{row["query_date"].strftime("%Y-%m-%d")}"
                    )
            """
            self.run_sql(sql, auto_commit=False)
            
        # Commit changes
        self.commit_close()
    
    def save_noncompliant_data(self, noncompliant_data: list):
        """ Save in database the no compliant data

        Args:
            noncompliant_data (list): dictionaries with no compliant data
            
            Structure:
            [
                 {
                    "company": str,
                    "deficiency": str,
                    "market": str,
                    "notification_date": datetime,
                },
                ...
            ]
        """
        
        tables = {
            "company": "noncompliant_companies",
            "deficiency": "noncompliant_deficiencies",
            "market": "noncompliant_markets",
        }
        
        if noncompliant_data:
            
            dict_tables_data = {}
            for noncompliant_row in noncompliant_data:

                self.__get_dict_tables_data__(
                    tables,
                    noncompliant_row,
                    dict_tables_data
                )

                # Save row data
                sql = f"""
                    INSERT INTO noncompliant (
                        company_id,
                        deficiency_id,
                        market_id,
                        notification_date,
                        premarket_id
                    ) values (
                        {dict_tables_data["company"][noncompliant_row["company"]]},
                        {dict_tables_data["deficiency"][noncompliant_row["deficiency"]]},
                        {dict_tables_data["market"][noncompliant_row["market"]]},
                        "{noncompliant_row["notification_date"].strftime("%Y-%m-%d")}",
                        {self.premarket_id}
                    )
                                        
                """
                self.run_sql(sql, auto_commit=False)

            # Commit changes
            self.commit_close()