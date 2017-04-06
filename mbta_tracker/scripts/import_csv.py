import csv, sqlite3

conn = sqlite3.connect("../db.sqlite3")
cursor = conn.cursor()

with open('stations.csv', 'r', encoding='utf-8', errors='ignore') as file:
    delim = csv.reader(file)
    to_db = [i for i in delim]

cursor.executemany("INSERT INTO realtime_station (name) VALUES (?);", to_db)
conn.commit()
conn.close()
