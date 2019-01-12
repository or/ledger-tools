#!/usr/bin/env python3
import argparse
import os
import tempfile
from configparser import ConfigParser
from datetime import date, datetime, timedelta

from absa import login
from common import get_elements, process_transactions

def download_transactions(browser, config, tmp_dir, from_date):
    from_date_value = from_date.strftime("%Y-%m-%d")
    wrapper = get_elements(browser, cls="ap-accounts-container")[0]
    original_window = browser.window_handles[0]
    for section in config.sections():
        if not section.startswith("account ") or config[section].get("type") != "absa":
            continue

        account_name = section.split(" ", 1)[1]
        account_number = config[section]["account"]
        header = get_elements(wrapper, cls="ap-accountbar", accountno=account_number)[0]
        header.click()
        from_date = get_elements(header, name="fromDate")[0]
        browser.execute_script("arguments[0].value = '{}'".format(from_date_value), from_date)
        search = get_elements(header, tag="button", tooltip="Filter by date")[0]
        search.click()
        download = get_elements(header, tag="button", tooltip="Download transaction history")[0]
        download.click()
        modal = get_elements(header, cls="ap-downloadTransactionHistory-modal", css_display="block")[0]
        download2 = get_elements(modal, cls="ap-button-next")[0]
        download2.click()
        process_transactions(config, account_name, tmp_dir + "/transactionHistory.csv")
        handles = browser.window_handles
        browser.switch_to_window(handles[-1])
        browser.close()
        browser.switch_to_window(original_window)
        close = get_elements(modal, cls="ui-modal-closeButton")[0]
        close.click()
        header2 = get_elements(header, cls="ap-titlebar")[0]
        header2.click()


def get_stats(browser):
    stats = []
    elements = get_elements(browser, cls="balance-field")
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

    os.makedirs("tmp", exist_ok=True)
    tmp_dir = tempfile.mkdtemp(dir="tmp")
    browser = login(config, tmp_dir=tmp_dir)

    download_transactions(browser, config, tmp_dir, args.from_date)

    browser.execute_script("window.scrollTo(0, 0)")
    logoff = get_elements(browser, cls="ui-link", text="Logoff")[0]
    logoff.click()

    stats = get_stats(browser)
    for s in stats:
        print(s)

    browser.close()
