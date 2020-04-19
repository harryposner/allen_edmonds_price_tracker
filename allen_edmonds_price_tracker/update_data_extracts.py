import json
import os
import os.path
import sqlite3


DB_PATH = os.path.join("data", "all_shoes_price_history.sqlite3")


query_current_shoes = """
    SELECT DISTINCT item_id, name, color
    FROM AllenEdmondsPrices
    WHERE date("now") - date(timestamp) <= 1
"""

# Once I have a long enough price history, I want to chart price over time
query_price_history = """
    SELECT timestamp, on_sale, regular_price, current_price
    FROM AllenEdmondsPrices
    WHERE item_id = ?
    ORDER BY timestamp ASC
"""

query_current_status = """
    SELECT timestamp, on_sale, regular_price, current_price
    FROM AllenEdmondsPrices
    WHERE item_id = :item_id
        AND datetime(timestamp) = (
            SELECT max(datetime(timestamp))
            FROM AllenEdmondsPrices
            WHERE item_id = :item_id
        )
"""


def update_json_extracts():
    conn = sqlite3.connect(DB_PATH)

    shoes = list(conn.execute(query_current_shoes))

    for item_id, name, color in shoes:
        shoe_dir = os.path.join("data", "current_status", name, color)
        if not os.path.exists(shoe_dir):
            os.makedirs(shoe_dir)
        status = next(conn.execute(query_current_status, {"item_id": item_id}))
        current_status = {
            "timestamp": status[0],
            "on_sale": status[1],
            "regular_price": status[2],
            "current_price": status[3],
        }
        with open(os.path.join(shoe_dir, "current_status.json"), "w") as fp:
            json.dump(current_status, fp)

    conn.close()

if __name__ == "__main__":
    update_json_extracts()
