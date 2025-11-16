"""
Export Green Button (ESPI) energy usage data from your Enbridge Gas account.
"""
import argparse
import enum
import getpass
import json
import logging
import os
import shutil
import sys
import time
import zipfile
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchDriverException

__version__ = '0.1.0'

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Browser(str, enum.Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'


def get_web_driver(browser: Browser) -> WebDriver:
    if browser == Browser.FIREFOX:
        options = webdriver.FirefoxOptions()
        # options.add_argument('--headless')
        # options.set_preference("browser.download.folderList", 2)
        # options.set_preference("browser.download.manager.showWhenStarting", False)
        # options.set_preference("browser.download.dir", "/tmp")
        # options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
        return webdriver.Firefox(options=options)
    else:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # options.add_experimental_option("prefs", {
        #     "download.default_directory": "/tmp",
        #     "download.directory_upgrade": True,
        #     "download.prompt_for_download": False,
        # })
        options.add_argument('--headless')
        try:
            #in case we are on x86_64 we do not need the chromeservice workaround,
            #so try the normal way first
            return webdriver.Chrome(options=options)
        except NoSuchDriverException:
            chromedriver_path = shutil.which("chromedriver") #/usr/bin/chromedriver
            service = webdriver.ChromeService(executable_path=chromedriver_path)
            return webdriver.Chrome(options=options, service=service)


def login(driver: WebDriver, username: str, password: str) -> None:
    """Log into the Enbridge Gas dashboard."""
    driver.get('https://myaccount.enbridgegas.com')

    time.sleep(1)

    username_field = driver.find_element('id', 'okta-signin-username')
    password_field = driver.find_element('id', 'okta-signin-password')
    login_button = driver.find_element('id', 'okta-signin-submit')

    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    # if URL redirects to MFA page, handle it here (not implemented)

    wait = WebDriverWait(driver, 60, ignored_exceptions=TimeoutError)
    wait.until(
        lambda driver: driver.current_url == 'https://myaccount.enbridgegas.com/OktaLoading?refreshUserContext=true' or driver.current_url == "https://myaccount.enbridgegas.com/my-account/my-bill"
    )
    
    time.sleep(1)

    mfa_field = driver.find_element('id', 'btnSkipMFA')
    mfa_field.click()

    time.sleep(1)

    skip_reward_button = driver.find_element('id', 'cancelNotification')
    skip_reward_button.click()

    wait = WebDriverWait(driver, 60)
    wait.until(
        lambda driver: driver.current_url == 'https://myaccount.enbridgegas.com/my-account/my-bill'
    )

def download_in_browser(driver: WebDriver, account_id: str, start_date: date, end_date: date) -> None:
    driver.set_page_load_timeout(10)
    try:
        driver.get(f'https://myaccount.enbridgegas.com/api/ShareMyData/Download?Service={account_id}&Category=Account,Billing,Usage&fromDate={start_date:%m/%d/%Y}&toDate={end_date:%m/%d/%Y}&log=false')
    except TimeoutException:
        pass  # Expected timeout since the download may take time

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__,
    )

    parser.add_argument(
        '--username',
        '-u',
        default=os.getenv('ENBRIDGE_GAS_USERNAME'),
        help='Enbridge Gas username. Will prompt if not set. [ENBRIDGE_GAS_USERNAME]',
    )
    parser.add_argument(
        '--password',
        '-p',
        default=os.getenv('ENBRIDGE_GAS_PASSWORD'),
        help='Enbridge Gas password. Will prompt if not set. [ENBRIDGE_GAS_PASSWORD]',
    )

    parser.add_argument(
        '--account-id',
        '-a',
        default=os.getenv('ENBRIDGE_GAS_ACCOUNT_ID'),
        help='Enbridge Gas account ID. [ENBRIDGE_GAS_ACCOUNT_ID]',
    )

    default_end_date = datetime.now().date() - timedelta(days=1)
    default_start_date = datetime.now().date() - timedelta(days=8)
    parser.add_argument(
        '--start-date',
        default=default_start_date,
        help=f'Fetch usage data from this date (inclusive, YYYY-mm-dd). Defaults to eight days ago ({default_start_date:%Y-%m-%d}).',
        type=clean_date,
    )
    parser.add_argument(
        '--end-date',
        default=default_end_date,
        help=f'Fetch usage data through this date (inclusive, YYYY-mm-dd). Defaults to one day ago ({default_end_date:%Y-%m-%d}).',
        type=clean_date,
    )

    parser.add_argument(
        '--browser',
        choices=[browser.value for browser in Browser],
        default=get_default_browser().value,
        help='Headless browser to use to access Enbridge Gas dashboard (default: %(default)s).',
        type=Browser,
    )
    parser.add_argument(
        '--output',
        '-o',
        metavar='OUTPUT',
        dest='out_file',
        default="enbridge_gas_data.xml",
        help='Write XML data to this file. Defaults to standard output.',
        type=argparse.FileType('w'),
    )

    args = parser.parse_args(argv)

    if args.start_date > args.end_date:
        raise argparse.ArgumentTypeError(
            f"end date '{args.end_date:%Y-%m-%d}' must be later than start date '{args.start_date:%Y-%m-%d}'"
        )

    return args


def get_default_browser() -> WebDriver:
    if shutil.which('chromedriver'):
        return Browser.CHROME
    else:
        return Browser.FIREFOX


def clean_date(value: str) -> date:
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f'{value!r} must be a date in ISO 8601 YYYY-mm-dd format'
        ) from exc


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    username = args.username or input('Username: ')
    password = args.password or getpass.getpass()
    account_id = args.account_id or input('Account ID: ')
    start_date = args.start_date or input('Start date (YYYY-MM-DD): ')
    end_date = args.end_date or input('End date (YYYY-MM-DD): ')

    try:
        logger.info('Starting Selenium web driver')
        driver = get_web_driver(args.browser)
        driver.set_page_load_timeout(120)
        logger.info('Logging into Enbridge Gas dashboard')
        login(driver, username, password)
        logger.info('Downloading data in browser')
        download_in_browser(driver, account_id, start_date, end_date)

        archive = zipfile.ZipFile('EGD_GAS_DownloadmyData.zip')
        data = archive.read('EGD_Gas_EnergyUsage_20251107_20251114.xml')
        print(data)
        print(str(data))
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
