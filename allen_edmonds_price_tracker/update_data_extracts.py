import os
import os.path
import sqlite3


DB_PATH = os.path.join("data", "all_shoes_price_history.sqlite3")


query_current_shoes = """
    SELECT DISTINCT item_id, name, color
    FROM AllenEdmondsPrices
    WHERE strftime('%d', 'now') - strftime('%d', timestamp) < 1
"""

query_price_history = """
    SELECT timestamp, on_sale, regular_price, current_price
    FROM AllenEdmondsPrices
    WHERE item_id = ?
    ORDER BY timestamp ASC
"""


conn = sqlite3.connect(DB_PATH)

with conn:
    shoes = list(conn.execute(query_current_shoes))

for item_id, name, color in shoes:
    shoe_dir = os.path.join("data", name, color)
    if not os.path.exists(shoe_dir):
        os.makedirs(shoe_dir)
    price_history = pd.read_sql(query_price_history, conn, params=(item_id, ))
    with open(os.path.join(shoe_dir, "current_status.json", "w")) as fp:
        fp.write(price_history.iloc[-1].to_json())


conn.close()
