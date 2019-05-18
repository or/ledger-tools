#!/usr/bin/env python3
import argparse
import os
import shutil
import tempfile
from configparser import ConfigParser
from datetime import date, datetime, timedelta
from selenium import webdriver

from common import load_credentials, get_elements, process_transactions

def login(config):
    credentials = load_credentials(config)
    os.makedirs("tmp", exist_ok=True)
    tmp_dir = tempfile.mkdtemp(dir="/tmp")
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": tmp_dir}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
    browser.get("https://www.dkb.de/banking")
    account = get_elements(browser, name='j_username', enabled=True)[0]
    pin = get_elements(browser, name='j_password', enabled=True)[0]
    account.send_keys(credentials["dkb.login"])
    pin.send_keys(credentials["dkb.pin"])
    pin.submit()

    return browser, tmp_dir


def download_transactions(browser, config, tmp_dir, from_date):
    from_date_value = from_date.strftime("%d.%m.%Y")
    browser.get("https://www.dkb.de/banking/finanzstatus/kontoumsaetze?$event=init")
    # for account_name, account_id, filename in accounts:
    for section in config.sections():
        if not section.startswith("account ") or config[section].get("type") != "dkb":
            continue

        account_name = section.split(" ", 1)[1]
        account_id = config[section]["id"]
        filename = config[section]["download_filename"]
        account_select = get_elements(browser, name="slAllAccounts")[0]
        browser.execute_script("arguments[0].value = '{}'".format(account_id), account_select)
        account_select.click()
        account_select.send_keys("\n")

        if account_name == "dkb-giro":
            search_period_name = "searchPeriodRadio"
            search_period = get_elements(browser, name=search_period_name)[1]
            transaction_date = get_elements(browser, name="transactionDate")[0]
        else:
            search_period_name = "filterType"
            search_period = get_elements(browser, name=search_period_name)[1]
            transaction_date = get_elements(browser, name="postingDate")[0]

        search_period.click()
        browser.execute_script("arguments[0].value = '{}'".format(from_date_value), transaction_date)

        if account_name == "dkb-creditcard":
            to_transaction_date = get_elements(browser, name="toPostingDate")[0]
            to_date_value = date.today().strftime("%d.%m.%Y")
            browser.execute_script("arguments[0].value = '{}'".format(to_date_value),
                                   to_transaction_date)

        search_button = get_elements(browser, id="searchbutton")[0]
        search_button.click()

        export_button = get_elements(browser, cls="iconExport0")[0]
        export_button.click()

        process_transactions(config, account_name, tmp_dir + "/" + filename)


def get_stats(browser):
    stats = []
    elements = get_elements(browser, cls="amount")
    for e in elements:
        stats.append(e.text)

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", "-d", required=False)

    args = parser.parse_args()
    if not args.from_date:
        args.from_date = date.today() - timedelta(days=60)
    else:
        args.from_date = datetime.strptime(args.from_date, "%Y-%m-%d").date()

    config = ConfigParser(interpolation=None)
    config.read("accounting.conf")

    browser, tmp_dir = login(config)
    stats = get_stats(browser)
    download_transactions(browser, config, tmp_dir, args.from_date)

    browser.get("https://www.dkb.de/DkbTransactionBanking/banner.xhtml?$event=logout")

    for s in stats:
        print(s)

    browser.close()
    shutil.rmtree(tmp_dir)
