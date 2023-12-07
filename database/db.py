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