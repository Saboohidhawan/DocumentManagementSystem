from db_sqlite import get_db, run_query

# DATABASE = 'document_manager.db'
def initialise_db(DATABASE):
	with get_db(DATABASE) as db:
		drop_table = '''DROP TABLE IF EXISTS users;'''
		create_table = '''CREATE TABLE users (
		  id INTEGER PRIMARY KEY AUTOINCREMENT,
		  user TEXT UNIQUE NOT NULL,
		  password TEXT NOT NULL
		);'''
		run_query(db, drop_table)	
		run_query(db, create_table)

		drop_table = '''DROP TABLE IF EXISTS documents;'''
		create_table = '''CREATE TABLE documents (
		  id INTEGER PRIMARY KEY AUTOINCREMENT,
		  filename TEXT UNIQUE NOT NULL
		);'''
		run_query(db, drop_table)	
		run_query(db, create_table)

		drop_table = '''DROP TABLE IF EXISTS document_users;'''
		create_table = '''CREATE TABLE document_users (
		  id INTEGER PRIMARY KEY AUTOINCREMENT,
		  doc_id INTEGER NOT NULL,
		  user_id INTEGER NOT NULL,
		  is_owner BOOLEAN NOT NULL CHECK (is_owner IN (0,1)),
		  is_editing BOOLEAN NOT NULL CHECK (is_editing IN (0,1))
		);'''
		run_query(db, drop_table)	
		run_query(db, create_table)

		users = [{'user':'user1','password':'user1'}, {'user':'user2','password':'user2'}, {'user':'user3','password':'user3'}]
		for dict in users:
			run_query(db, ''' INSERT INTO users (user, password) VALUES (?,?) ''', (dict['user'], dict['password']))