import csv

import fdb

conn = fdb.connect(dsn='localhost:d:\DATABASE.FDB', user='sysdba', password='masterkey')
cursor = conn.cursor()
with open('nomenk.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';',  quotechar='\'')
    for prod in spamreader:
        print(prod[7])
        sql = "insert into production " \
              "(id, group_name, name, descr, ingridients, storage_conditions, " \
              "nutritional_value, energy_value, RC_BY, TU_BY, STB, " \
              "expiration_date, bar_code, code128_prefix) " \
              "values" \
              f"({prod[0]}, '{prod[1]}', '{prod[2]}', '{prod[3]}', '{prod[5]}', '{prod[6]}', " \
              f"'{prod[8]}', '{prod[12]}', '{prod[9]}', '{prod[10]}', '{prod[11]}', " \
              f"'{prod[4]}', '{prod[7]}', 22)"
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
           conn.rollback()
           print(e)
