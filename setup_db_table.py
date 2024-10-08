import sqlite3
con = sqlite3.connect("adv.db")

cur = con.cursor()
cur.execute('''CREATE TABLE Advertisement(
    adv_id,
    user_id,
    username,
    first_name,
    last_name
    )''')
