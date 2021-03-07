from db_sqlite import get_db, run_query, query_db

DATABASE = 'document_manager.db'
with get_db(DATABASE) as db:
	for table in ['users', 'documents', 'document_users']:
		print(f"\nTable '{table}' details:")
		users = query_db(db, f'SELECT * FROM {table}')
		for user in users:
			print(dict(user))
	#run_query(db, ''' UPDATE document_users set is_editing=? WHERE doc_id=? and user_id=? ''', (0,3,2))
	#run_query(db, ''' UPDATE document_users set is_editing=? WHERE doc_id=? and user_id=? ''', (0,3,1))
	#run_query(db, ''' DELETE FROM documents where id = ?''', (2,))
	#run_query(db, ''' DELETE FROM document_users where doc_id = ?''', (2,))