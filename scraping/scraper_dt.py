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
            "new_filings": "https://dilutiontracker.com/app/new?a=t3vcol"
        }

        # Start chrome instance with chrome data
        super().__init__(
            chrome_folder=chrome_folder,
            start_killing=True,
        )

    def __get_table_data__(self, selector_rows: str, columns: dict,
                           start_row: int = 1, end_row: int = -1) -> list:
        """ get data from table structure

        Args:
            selector_rows (str): selector of each row of table
            columns (dict): column data: selector, datatype and optional extra
            start_row (int, optional): start row index (inclusive). Defaults to 1
            end_row (int, optional): end row index (no inclusive). Defaults to -1

        Returns:
            list: table data with dynamic structure (based on column dict)
        """

        data = []

        rows_num = len(self.get_elems(selector_rows))
        for index in range(rows_num):

            # End loop if end row is reached
            if index + start_row == end_row:
                break

            selector_row = f'{selector_rows}:nth-child({index + start_row})'

            data_row = {}
            for colum_name, column_data in columns.items():

                selector_column = f'{selector_row} {column_data["selector"]}'
                data_type_column = column_data["data_type"]

                # Extract links
                extra = column_data.get("extra", {})
                if extra.get("is_link", False):
                    value = self.get_attrib(selector_column, "href")
                    data_row[colum_name] = value
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
                    data_row[colum_name] = "NULL"
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

                data_row[colum_name] = value

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
        
        print("Scrapeing table New Filings")
        
        self.set_page(self.pages["new_filings"])
        self.refresh_selenium()
        
        # Get table data
        table_data = self.__get_table_data__(
            selector_rows="tbody > tr",
            columns={
                "ticker": {
                    "selector": 'td:nth-child(1)',
                    "data_type": str,
                },
                "company_name": {
                    "selector": 'td:nth-child(2)',
                    "data_type": str,
                },
                "dilution_type": {
                    "selector": 'td:nth-child(3)',
                    "data_type": str,
                },
                "dilution_name": {
                    "selector": 'td:nth-child(4)',
                    "data_type": str,
                },
                "date_modified": {
                    "selector": 'td:nth-child(5)',
                    "data_type": dt,
                    "extra": {"format": "%Y-%m-%d"}
                }
            }
        )
        print(table_data)

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
