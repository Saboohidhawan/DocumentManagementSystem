import sqlite3

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db(DATABASE):
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    #db.row_factory = make_dicts
    return db


def run_query(db, query, args = ()):
    cur = db.cursor().execute(query, args)
    db.commit()
	
	
def query_db(db, query, args=(), one=False):
    cur = db.cursor().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows