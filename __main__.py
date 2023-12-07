import os
from dotenv import load_dotenv
from logs import logger
from scraping.scraper_dt import ScrapingDilutionTracker
# from database.db import Database
load_dotenv()

DEBUG = os.getenv("DEBUG") == "True"
CHROME_FOLDER = os.getenv('CHROME_FOLDER')


def main():

    # Connect to database
    # database = Database()

    # Validate chrome folder
    if CHROME_FOLDER is None or not os.path.isdir(CHROME_FOLDER):
        logger.error('CHROME_FOLDER not found env variable is not set')
        quit()

    # Connect to dilution tracker
    scraper = ScrapingDilutionTracker(CHROME_FOLDER)

    # End if login failed
    is_logged = scraper.login()
    if is_logged:
        logger.info('Login success')
    else:
        error_message = 'Login failed. Close the program, open chrome, ' \
                        'login manually and try again'
        logger.error(error_message)
        quit()
        
    # Get new filings
    new_filings = scraper.get_new_filings()
    print(new_filings)


if __name__ == '__main__':
    main()