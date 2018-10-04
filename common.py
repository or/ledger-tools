import os
import subprocess
import time
from datetime import date
from selenium.common.exceptions import NoSuchElementException

def load_credentials(config):
    """
    Decrypts the accounting keys file with GPG.
    File should have this format:
    ------
    absa.login <login-name>
    absa.pin <login-pin>
    absa.password <password>
    dkb.login <login-name>
    dkb.password <password>
    [<other>.login <login-name>]
    [<other>.password <password>]
    ------
    and be encrypted, for instance, like so:
    % gpg -c -o accounting.keys.gpg accounting.keys
    to use a symmetric encryption with password, or use a public key
    encryption.

    It will be decrypted like so:
    % gpg -q -d accounting.keys.gpg
    """
    credentials = {}
    output = subprocess.check_output(["gpg", "-q", "-d", config["general"]["key_file"]])
    for line in output.decode("utf-8").split("\n"):
        line = line.strip()
        if not line:
            continue

        key, value = list(map(lambda x: x.strip(), line.split(" ", 1)))
        credentials[key] = value

    return credentials


def _get_elements(parent, **kwargs):
    if "id" in kwargs:
        elements = [parent.find_element_by_id(kwargs["id"])]

    elif "name" in kwargs:
        elements = parent.find_elements_by_name(kwargs["name"])

    elif "tag" in kwargs:
        elements = parent.find_elements_by_tag_name(kwargs["tag"])

    elif "cls" in kwargs:
        elements = parent.find_elements_by_class_name(kwargs["cls"])

    else:
        raise Exception("need at least id, name, or cls")

    filtered_elements = []
    for e in elements:
        use = True
        for k, v in kwargs.items():
            if k in ["id", "tag"]:
                continue

            elif k == "enabled":
                if e.is_enabled() != v:
                    use = False
                    continue

            elif k == "cls":
                if v not in e.get_attribute("class").split():
                    use = False
                    continue

            elif k == "text":
                if str(e.text).strip() != v:
                    use = False
                    continue

            elif k.startswith("css_"):
                if e.value_of_css_property(k[4:]) != v:
                    use = False
                    continue

            else:
                k = k.replace("_", "-")
                if e.get_attribute(k) != v:
                    use = False
                    continue

        if use:
            filtered_elements.append(e)

    if not filtered_elements:
        raise NoSuchElementException()

    return filtered_elements


def get_elements(parent, **kwargs):
    print("finding element {}...".format(kwargs))
    t = time.time()
    timeout = kwargs.get("timeout", None)
    if timeout:
        timeout = int(timeout)

    for i in range(300):
        try:
            return _get_elements(parent, **kwargs)

        except NoSuchElementException:
            time.sleep(0.1)

        if timeout and time.time() - t >= timeout:
            return None

    raise Exception("giving up, waiting for element {}...".format(kwargs))


def process_transactions(config, account_name, path):
    for i in range(300):
        if os.path.exists(path):
            break

        time.sleep(0.1)

    if not os.path.exists(path):
        raise Exception("couldn't find {} even after waiting...".format(path))

    if account_name.startswith("dkb"):
        delimiter = ";"
    else:
        delimiter = ","

    os.makedirs(config["general"]["transaction_dir"], exist_ok=True)
    year = date.today().year
    transaction_filename = \
        os.path.join(config["general"]["transaction_dir"],
                     "{name}-{year}.csv".format(name=account_name, year=year))
    if not os.path.exists(transaction_filename):
        current_file = ""
    else:
        current_file = open(transaction_filename, "rb").read().decode("utf-8")

    existing_lines = set()
    for line in current_file.split("\n"):
        line = line.strip()
        if not line:
            continue

        if account_name == "dkb-creditcard":
            line = line.split(delimiter, 1)[1]

        existing_lines.add(line.lower())

    new_file = open(path, "rb").read().decode("latin1")
    current_file = open(transaction_filename, "ab")
    for line in new_file.split("\n")[1:]:
        line = line.strip()
        if line.count(delimiter) < 3:
            continue

        check = line
        if account_name == "dkb-creditcard":
            check = check.split(delimiter, 1)[1]

        if check.lower() in existing_lines:
            continue

        current_file.write((line + "\n").encode("utf-8"))

    current_file.close()
    os.remove(path)
