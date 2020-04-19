import csv
import datetime
import json
import os.path
import sqlite3
import time

import requests
from bs4 import BeautifulSoup


COURTESY_DELAY = 1
CSV_PATH = os.path.join("data", "all_shoes_price_history.csv")
DB_PATH = os.path.join("data", "all_shoes_price_history.sqlite3")
ALL_SHOES_URL = "https://www.allenedmonds.com/shoes/"


def get(*args, **kwargs):
    time.sleep(COURTESY_DELAY)
    resp = requests.get(*args, **kwargs)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def shoe_info(grid_tile_tag):
    tag = grid_tile_tag.find("div")
    timestamp = datetime.datetime.utcnow().isoformat()
    tile_id = tag["id"]
    item_id = tag["data-itemid"]

    name_tag = tag.find("a", class_="name-link")
    name = name_tag.text.strip()
    shoe_url = name_tag["href"]

    swatch_tag = tag.find("a", class_="swatch selected")
    if swatch_tag is not None:
        swatch_info = swatch_tag.find("img")["data-thumb"]
        color = json.loads(swatch_info)["title"][len(name) + 2:]
    else:
        shoe_soup = get(shoe_url)
        color_tag = shoe_soup.find("span", id="clrName")
        color = color_tag.text.strip()

    regular_price_tag = tag.find("span", class_="product-regular-price")
    on_sale = int(regular_price_tag is None)
    if on_sale:
        regular_price = tag.find("span", class_="product-standard-price").text
        current_price = tag.find("span", class_="product-sales-price").text
    else:
        regular_price = current_price = regular_price_tag.text
    regular_price = regular_price.lstrip("$")
    current_price = current_price.lstrip("$")

    info = (
            timestamp,
            tile_id,
            item_id,
            name,
            shoe_url,
            color,
            on_sale,
            regular_price,
            current_price,
            )

    return info


def update_prices():
    n_items = int(get(ALL_SHOES_URL)
            .find("div", class_="results-hits")
            .find("span", class_="current-page-label desktop")
            .text
            .split()[0]
            )

    shoes = []
    for start in range(0, n_items, 18):
        soup = get(ALL_SHOES_URL, params={"start": start, "sz": "18"})
        for grid_tag in soup.find_all("li", class_="grid-tile"):
            shoes.append(shoe_info(grid_tag))


    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS AllenEdmondsPrices
                (
                    timestamp TEXT,
                    tile_id TEXT,
                    item_id TEXT,
                    name TEXT,
                    url TEXT,
                    color TEXT,
                    on_sale INTEGER,
                    regular_price TEXT,
                    current_price TEXT
                )
            """)

    insert = "INSERT INTO AllenEdmondsPrices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    with conn:
        conn.executemany(insert, shoes)

    conn.close()

    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as fp:
            col_names = [
                    "timestamp",
                    "tile_id",
                    "item_id",
                    "name",
                    "url",
                    "color",
                    "on_sale",
                    "regular_price",
                    "current_price",
                    ]
            csv.writer(fp).writerow(col_names)

    with open(CSV_PATH, "a", newline="") as fp:
        csv.writer(fp).writerows(shoes)


if __name__ == "__main__":
    update_prices()
