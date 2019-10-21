from common import load_credentials, get_elements
from selenium import webdriver


def login(config, tmp_dir=None):
    credentials = load_credentials(config)
    chrome_options = webdriver.ChromeOptions()
    prefs = {}
    if tmp_dir:
        prefs["download.default_directory"] = tmp_dir

    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path='chromedriver',
                               chrome_options=chrome_options)
    browser.get("https://ib.absa.co.za/absa-online/login.jsp")

    account = get_elements(browser, name='AccessAccount', enabled=True)[0]
    pin = get_elements(browser, name='PIN', enabled=True)[0]
    next_button = get_elements(browser, cls="ap-button-next", enabled=True)[0]
    # make sure the blocking overlay is gone
    get_elements(browser, id='pleasewait', css_display="none")[0]
    #print(credentials)
    account.send_keys(credentials["absa.login"])
    pin.send_keys(credentials["absa.pin"])
    next_button.click()

    captcha = get_elements(browser, id='ui-row-captcha', enabled=True,
                           timeout=2)
    if captcha:
        account = get_elements(browser, name='AccessAccount', enabled=True)[0]
        pin = get_elements(browser, name='PIN', enabled=True)[0]
        captcha = get_elements(browser, name='CaptchaTxt', enabled=True)[0]
        account.send_keys(credentials["absa.login"])
        pin.send_keys(credentials["absa.pin"])
        captcha.send_keys(input("captcha? "))
        captcha.submit()

    ui_select = get_elements(browser, cls="ui-select")[0]
    browser.execute_script("arguments[0].value = 'accounts'", ui_select)
    ui_select.click()
    ui_select.send_keys("\n")

    absa_password = credentials["absa.password"]
    pf1 = get_elements(browser, id="pff1", enabled=True)[0]
    pf2 = get_elements(browser, id="pff2", enabled=True)[0]
    pf3 = get_elements(browser, id="pff3", enabled=True)[0]

    for pf in [pf1, pf2, pf3]:
        pos = int(pf.get_attribute("num")) - 1
        pf.send_keys(absa_password[pos])

    pf3.submit()

    return browser
