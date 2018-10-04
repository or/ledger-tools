#!/usr/bin/env python3
from configparser import ConfigParser

from absa import login


if __name__ == "__main__":
    config = ConfigParser()
    config.read("accounting.conf")
    browser = login(config)
