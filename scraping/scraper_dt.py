from time import sleep
from datetime import datetime as dt
from scraping.web_scraping import WebScraping


class ScrapingDilutionTracker (WebScraping):

    def __init__(self, chrome_folder: str):
        """ Connect to WebScraping class and start chrome instance

        Args:
            chrome_folder (str): chrome data folder path
        """

        # Scraping pages
        self.pages = {
            "home": "https://dilutiontracker.com",
            "new_filings": "https://dilutiontracker.com/app/new?a=t3vcol",
            "completed_offering": "https://dilutiontracker.com/app/completed-offerings",
            "pending_s1s": "https://dilutiontracker.com/app/s1"
        }

        # Start chrome instance with chrome data
        super().__init__(
            chrome_folder=chrome_folder,
            start_killing=True,
        )

    def __get_table_data__(self, columns: list,
                           start_row: int = 1, end_row: int = -1) -> list:
        """ get data from table structure

        Args:
            selector_rows (str): selector of each row of table
            columns (list): dicts with column data: column name and ata type
            start_row (int, optional): start row index (inclusive). Defaults to 1
            end_row (int, optional): end row index (no inclusive). Defaults to -1

        Returns:
            list: table data with dynamic structure (based on column dict)
        """

        data = []
        selector_rows = "tbody > tr"
        rows_num = len(self.get_elems(selector_rows))
        for index in range(rows_num):
            
            # End loop if end row is reached
            if index + start_row == end_row:
                break

            # Generate row selector
            selector_row = f'{selector_rows}:nth-child({index + start_row})'
            
            # auto detect end row
            row = self.get_elems(selector_row)
            if not row:
                break

            data_row = {}
            last_double_column = False
            double_columns_found = 0
            for column_data in columns:
                
                # Get column name and data type
                column_name = column_data["name"]
                data_type_column = column_data["data_type"]
                
                # Generate column selector
                row_index = columns.index(column_data) + 1 - double_columns_found
                selector_column = f'{selector_row} td:nth-child({row_index})'
                
                # Detect colspan=2
                colspan = self.get_attrib(selector_column, "colspan")

                # Skip if last column was double
                if last_double_column:
                    data_row[column_name] = "NULL"
                    last_double_column = False
                    continue

                # Extract links
                extra = column_data.get("extra", {})
                if extra.get("is_link", False):
                    value = self.get_attrib(selector_column, "href")
                    data_row[column_name] = value
                    continue

                # Extract texts
                replace_chats = [
                    "\\",
                    "'",
                    '"'
                ]
                value = self.get_text(selector_column)
                for chat in replace_chats:
                    value = value.replace(chat, "")

                # Skip empty values
                if not value:
                    data_row[column_name] = "NULL"
                    continue

                # Convert numeric fields
                if data_type_column in [int, float]:
                    value = value.replace(",", "").replace(
                        "%", "").replace("$", "")

                # Convert date format 2023-09-30
                if data_type_column == dt:

                    # Get format frome extra data
                    format_date = column_data["extra"]["format"]
                    value = dt.strptime(value, format_date)

                data_row[column_name] = value
                
                # Skip next column if colspan=2
                if colspan == "2":
                    last_double_column = True
                    double_columns_found += 1

            # Add query date to data
            data_row["query_date"] = dt.today()

            data.append(data_row)

        return data

    def login(self) -> bool:
        """ Validate correct login and go to app page

        Returns:
            bool: True if login success
        """

        selectors = {
            "nav_items": 'nav li',
            "close_modal": '.intercom-post-close'
        }

        # Load home page
        self.set_page(self.pages["home"])
        self.refresh_selenium()

        # Validte if exists "go to app" button
        go_to_app_found = False
        buttons_texts = self.get_texts(selectors["nav_items"])
        if "Go to App" in buttons_texts:

            # Go to home page
            old_page = self.driver.current_url
            self.set_page(f'{self.pages["home"]}/app')
        
            go_to_app_found = True
            
        # Detect if login failed
        if not go_to_app_found:
            return False

        # Validate page change
        current_page = self.driver.current_url
        if old_page == current_page:
            return False

        # Close modal
        modal_elem = self.get_elems(selectors["close_modal"])
        if modal_elem:
            self.click_js(selectors["close_modal"])
            self.refresh_selenium()

        return True
    
    def get_new_filings(self) -> list:
        """ Extract data from tablle of new filings page

        Returns:
            list: dicts with rows data
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
        
        print("Scraping table New Filings")
        
        self.set_page(self.pages["new_filings"])
        self.refresh_selenium()
        
        # Get table data
        table_data = self.__get_table_data__(
            columns=[
                {
                    "name": "ticker",
                    "data_type": str,
                },
                {
                    "name": "company_name",
                    "data_type": str,
                },
                {
                    "name": "dilution_type",
                    "data_type": str,
                },
                {
                    "name": "dilution_name",
                    "data_type": str,
                },
                {
                    "name": "date_modified",
                    "data_type": dt,
                    "extra": {
                        "format": "%Y-%m-%d"
                    }
                }
            ]
        )
        return table_data
    
    def get_completed_offerings(self) -> list:
        """ Extract data from tablle of completed offering page

        Returns:
            list: dicts with rows data
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
                }
                ...
            ]
        """
        
        print("Scraping table Completed Offering")
        
        self.set_page(self.pages["completed_offering"])
        self.refresh_selenium()
        
        # Get table data
        table_data = self.__get_table_data__(
            columns=[
                {
                    "name": "ticker",
                    "data_type": str,
                },
                {
                    "name": "type",
                    "data_type": str,
                },
                {
                    "name": "method",
                    "data_type": str,
                },
                {
                    "name": "share_equivalent",
                    "data_type": int,
                },
                {
                    "name": "price",
                    "data_type": float,
                },
                {
                    "name": "warrants",
                    "data_type": int,
                },
                {
                    "name": "offering_amt",
                    "data_type": int,
                },
                {
                    "name": "bank",
                    "data_type": str,
                },
                {
                    "name": "investors",
                    "data_type": str,
                },
                {
                    "name": "datetime",
                    "data_type": dt,
                    "extra": {
                        "format": "%Y-%m-%d %H:%M",
                    }
                }
            ]
        )
        return table_data

    def get_pending_s1s(self) -> list:
        """ Extract data from tablle of new filings page

        Returns:
            list: dicts with rows data
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
        
        print("Scraping table Pending S1s")
        
        self.set_page(self.pages["pending_s1s"])
        self.refresh_selenium()
        
        # Get table data
        table_data = self.__get_table_data__(
            columns=[
                {
                    "name": "ticker",
                    "data_type": str,
                },
                {
                    "name": "company_name",
                    "data_type": str,
                },
                {
                    "name": "industry",
                    "data_type": str,
                },
                {
                    "name": "date_first_s1",
                    "data_type": dt,
                    "extra": {
                        "format": "%Y-%m-%d"
                    }
                },
                {
                    "name": "pricing_date",
                    "data_type": dt,
                    "extra": {
                        "format": "%Y-%m-%d"
                    }
                },
                {
                    "name": "anticipated_deal_size",
                    "data_type": str,
                },
                {
                    "name": "estimated_warrant_coverage",
                    "data_type": int,
                },
                {
                    "name": "underwriters_placement_agents",
                    "data_type": str,
                },
                {
                    "name": "float_before_offering",
                    "data_type": int,
                },
                {
                    "name": "status",
                    "data_type": str,
                },
                {
                    "name": "pricing",
                    "data_type": float,
                },
                {
                    "name": "shares_offered",
                    "data_type": int,
                },
                {
                    "name": "final_warrant_coverage",
                    "data_type": int,
                },
                {
                    "name": "exercise_price",
                    "data_type": float,
                },
            ],
            start_row=2
        )
        return table_data
    
    def get_noncompliant_data(self, tricker: str) -> list:
        """ Get data from noncompliantcompanylist page
        
        Args:
            tricker (str): company tricker (identifier)

        Returns:
            list: no complaint data

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

        selectors = {
            "dispay_btn": 'th [type="button"]',
            "rows": '.rgMasterTable tbody tr',
            "company": 'td[colspan="4"] p',
            "tricker": 'td:nth-child(2)',
            "deficiency": 'td:nth-child(3)',
            "market": 'td:nth-child(4)',
            "notification_date": 'td:nth-child(5)',
        }

        # Load page and open registers
        self.set_page(
            "https://listingcenter.nasdaq.com/noncompliantcompanylist.aspx")
        self.click_js(selectors["dispay_btn"])
        sleep(5)
        self.refresh_selenium()

        # Loop each row
        rows_num = len(self.get_elems(selectors["rows"]))
        current_company = ""
        data = []
        for index in range(rows_num):

            selector_row = f'{selectors["rows"]}:nth-child({index + 1})'
            selector_company = f'{selector_row} {selectors["company"]}'

            # Detect new company
            company = self.get_text(selector_company)
            if company:
                current_company = company
                continue

            # Validate company tricker
            selector_tricker = f'{selector_row} {selectors["tricker"]}'
            current_tricker = self.get_text(selector_tricker).lower().strip()
            if tricker not in current_tricker:
                continue
            
            # Extract row data
            selector_deficiency = f'{selector_row} {selectors["deficiency"]}'
            selector_market = f'{selector_row} {selectors["market"]}'
            selector_notification = f'{selector_row} {selectors["notification_date"]}'

            deficiency = self.get_text(selector_deficiency)
            market = self.get_text(selector_market)
            notification_date = self.get_text(selector_notification)

            # Format date
            notification_date = dt.strptime(notification_date, "%m/%d/%Y")

            # Save data
            data.append({
                "company": current_company,
                "deficiency": deficiency,
                "market": market,
                "notification_date": notification_date,
            })

        return data
