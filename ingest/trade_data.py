import requests
import pandas as pd

BASE_URL = "https://comtradeapi.un.org/data/v1/get"


def fetch_trade_data(
    product_code: str, country_code: str, year: int, max_results: int = 500
):
    params = {}
