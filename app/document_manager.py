import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_httpauth import HTTPBasicAuth
from db_sqlite import get_db, run_query, query_db
from initialise_db import initialise_db

DATABASE = 'document_manager.db'
initialise_db(DATABASE)#Resets the tables 'documents' and 'document_users' of database and stores details of dummy users in 'users' table.

ALLOWED_EXTENSIONS = {'txt', 'log'}

UPLOAD_FOLDER = "./upload_folder"
if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "super secret key"

auth = HTTPBasicAuth()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
	
@auth.verify_password
def verify_password(username, password):
	with get_db(DATABASE) as db:
		id = query_db(db, '''SELECT id FROM users WHERE (user, password) = (?,?)''',[username, password], one=True)
		if id:
			return id[0]
	return None


@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route("/documents", methods = ['GET'])
@auth.login_required
def list_files():
	"""List files on the server accessible to the user."""
	files = []
	with get_db(DATABASE) as db:
		accessible_files = query_db(db, '''SELECT doc_id FROM document_users WHERE user_id = ?''',[auth.current_user()])
		for docs in accessible_files:
			doc_ids = dict(docs)
			filename = query_db(db, '''SELECT filename FROM documents WHERE id = ?''',[doc_ids['doc_id']], one=True)[0]
			files.append(filename)
	return jsonify(files), 200
	

@app.route('/documents', methods = ['POST'])
@auth.login_required
def upload_file():
	"""Upload a file of allowed_extensions to the server if it isn't present there already."""

	if 'file' not in request.files or request.files['file'].filename == "":
		return jsonify('Missing file.'), 400

	f = request.files['file']		
	if allowed_file(f.filename):
		filename = secure_filename(f.filename)
		with get_db(DATABASE) as db:
			try:
				add_to_documents = ''' INSERT INTO documents (filename) VALUES (?) '''
				run_query(db, add_to_documents, args = (filename,))
				doc_id = query_db(db, '''SELECT id FROM documents WHERE filename = ?''',[filename], one=True)[0]
				add_to_document_users = ''' INSERT INTO document_users (doc_id, user_id, is_owner, is_editing) VALUES (?,?,?,?) '''
				run_query(db, add_to_document_users, [doc_id, auth.current_user(), 1, 0])
				
			except Exception as e:
				print(f"Exception in uploading file {filename} to the server: {e}")
				return jsonify('File already exists.'), 409
			else:
				f.save(os.path.join(UPLOAD_FOLDER,filename))
				return jsonify('File uploaded successfully.'), 201

	return jsonify(f'Unsupported File Extension. Allowed file types are {ALLOWED_EXTENSIONS}.'), 400
		

@app.route('/document_users', methods = ['POST'])
@auth.login_required
def share_file():
	"""Owner to Share a file with other users."""
	if request.data:
		#print(request.get_json())
		doc_id = request.get_json().get('doc_id')
		user_id = request.get_json().get('user_id')
		if not doc_id or not user_id:
			return jsonify("Invalid Request. Missing doc_id or user_id"), 400
		with get_db(DATABASE) as db:
			
			is_valid_doc = query_db(db, '''SELECT filename FROM documents WHERE id = ?''',[doc_id], one = True)
			if not is_valid_doc:
				return jsonify("File doesn't exist."), 400
				
			is_owner = query_db(db, '''SELECT is_owner FROM document_users WHERE (doc_id, user_id) = (?,?)''',[doc_id, auth.current_user()], one = True)[0]
			if is_owner == 0:
				return jsonify("Permission Denied!Only owner can share file."), 403
				
			is_valid_user = query_db(db, '''SELECT user FROM users WHERE id = ?''',[user_id], one = True)
			if not is_valid_user:
				return jsonify("Invalid user id. User doesn't exist."), 400
		
			is_already_shared = query_db(db, '''SELECT id FROM document_users WHERE (doc_id, user_id) = (?,?)''',[doc_id, user_id], one = True)
			if is_already_shared:
				return jsonify("File is already shared with the user"), 409
				
			add_to_document_users = ''' INSERT INTO document_users (doc_id, user_id, is_owner, is_editing) VALUES (?,?,?,?) '''
			run_query(db, add_to_document_users, [doc_id, user_id, 0, 0])
			return jsonify("Successfully shared the file."),200
			
	return jsonify("Invalid Request. Missing doc_id and user_id"), 400


@app.route("/documents/<path:doc_id>")
@auth.login_required
def download_file(doc_id):
	"""Download a file if it's not being edited by owner."""
	with get_db(DATABASE) as db:
	
		is_valid_file = query_db(db, '''SELECT is_editing FROM document_users WHERE (doc_id, is_owner) = (?,?)''',[doc_id, 1], one = True)
		if not is_valid_file:
			return jsonify("Invalid file id."), 400

		is_user_allowed = query_db(db, '''SELECT id FROM document_users WHERE (doc_id, user_id) = (?,?)''',[doc_id, auth.current_user()], one = True)
		if not is_user_allowed:
			return jsonify("Access Denied!"), 403
		
		is_owner_editing = is_valid_file[0]
		if is_owner_editing == 0:
			filename = query_db(db, '''SELECT filename FROM documents WHERE id = ?''',[doc_id], one=True)[0]
			return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
		return jsonify("Owner is editing. Please try after some time."), 409


@app.route("/documents/<doc_id>", methods=["PUT"])
@auth.login_required
def edit_file(doc_id):
	"""Edit a file if it's not being edited by other user."""
	if request.data:
		with get_db(DATABASE) as db:
	
			is_user_allowed = query_db(db, '''SELECT id FROM document_users WHERE (doc_id, user_id) = (?,?)''',[doc_id, auth.current_user()], one = True)
			if not is_user_allowed:
				return jsonify("Access Denied!"), 403
				
			is_valid_file = query_db(db, '''SELECT filename FROM documents WHERE (id) = (?)''',[doc_id], one = True)
			if not is_valid_file:
				return jsonify("Invalid file id."), 400
				
			editing = query_db(db, '''SELECT id FROM document_users WHERE (doc_id, is_editing) = (?,?)''',[doc_id, 1], one = True)
			if editing:
				return jsonify("File is being edited."), 409

			filename = is_valid_file[0]
			run_query(db, ''' UPDATE document_users set is_editing=? WHERE doc_id=? and user_id=? ''', (1, doc_id, auth.current_user()))
			with open(os.path.join(UPLOAD_FOLDER, filename), "ab") as fp:
				fp.write(request.data)
			with open(os.path.join(UPLOAD_FOLDER, filename), "a") as fp:
				fp.write('\n')
			run_query(db, ''' UPDATE document_users set is_editing=? WHERE doc_id=? and user_id=? ''', (0, doc_id, auth.current_user()))
			return jsonify("File Edited Successfully!"), 201
	return jsonify("No new data entered to edit!"), 400

			
@app.route("/documents/<doc_id>", methods=["DELETE"])
@auth.login_required
def delete_file(doc_id):
	"""Only Owner can delete a file."""
	with get_db(DATABASE) as db:
	
		is_valid_file = query_db(db, '''SELECT filename FROM documents WHERE (id) = (?)''',[doc_id], one = True)
		if not is_valid_file:
			return jsonify("Invalid file id."), 400
			
		is_owner = query_db(db, '''SELECT is_owner FROM document_users WHERE (doc_id, user_id) = (?,?)''',[doc_id, auth.current_user()], one = True)
		if not is_owner:
			return jsonify("Permission Denied! Only owner can delete a document."), 403
			
		editing = query_db(db, '''SELECT id FROM document_users WHERE (doc_id, is_editing) = (?,?)''',[doc_id, 1], one = True)
		if editing:
			return jsonify("File is being edited."), 409

		filename = is_valid_file[0]
		os.remove(os.path.join(UPLOAD_FOLDER, filename))
		run_query(db, ''' DELETE FROM documents where id = ?''', (doc_id,))
		run_query(db, ''' DELETE FROM document_users where doc_id = ?''', (doc_id,))						
		return jsonify("File Deleted Successfully!"), 200


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=False, port=5000)