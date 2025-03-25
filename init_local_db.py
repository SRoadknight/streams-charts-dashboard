import duckdb

url = "https://drive.google.com/uc?id=1BOyUZj7QsBMi5JTNp1oxhkXfANCWPkkR"
conn = duckdb.connect("local_streamer.db")
conn.execute(f"CREATE OR REPLACE TABLE channel_stats AS SELECT * FROM read_csv_auto('{url}')")
conn.sql("SELECT DISTINCT year FROM channel_stats").show()
conn.close()

