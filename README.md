# DOCUMENT MANAGEMENT SYSTEM

#### FUNCTIONALITY
This is the compilation of document management system APIs using python's module flask and database sqlite.

It requires HTTP Basic Authentication to perform following functions:
* Upload file. One who uploads the file becomes an owner.
* Download file. Those with whom the document has been shared can download the document if it's not being edited by owner at that time.
* Edit file. Those with whom the document has been shared can edit the document if it's not being edited by someone else. 
* Delete file. Only an owner can delete a file if it's not being edited by someone else at that time.
* Share a file with another user. Only an owner can share a file with another user.

#### LIMITATION
For editing a file, you can append to the already existing file but can't reupload a new version of the file with same filename. i.e. A file can be uploaded only once. If you wish to reupload, you need to first delete it and then upload. However, only an owner can delete.

---
#### SWAGGER
All the information related to APIs is available in swagger-dms.json and can be viewed by importing this file at editor.swagger.io.

---
#### DATABASE TABLES
* users: It contains information about username and passwords.
* documents: It contains information about all the documents present in the server.
* document_users: It contains information regarding which documents are shared with which user and owner of the document as well whether document is currently being edited or not.

---
#### CODE FILES
* document_manager.py : It starts the server and you can access these APIs through postman.
* initialise_db.py : This resets and creates the database tables and inserts dummy users to users table.
* db_sqlite.py : It contains functions for querying sqlite database.
* view_db.py : This is extra utility to check entries of various tables of database.

---
#### STEPS TO RUN LOCALLY

##### Dependencies:
Python version >=3.6.8
pip install flask
pip install flask_httpauth

##### Start the server
Update the UPLOAD_FOLDER in document_manager.py file and you are good to go.
python document_manager.py
```
├── app
│   ├── document_manager.py
│   └── db_sqlite.py
│   └── initialise_db.py
└── README.md
```
##### View Database Entries
python view_db.py
```
├── app
│   ├── view_db.py
│   └── db_sqlite.py
└── README.md
```
---
#### STEPS TO RUN AS A DOCKER CONTAINER
```
docker build -t document_manager .
docker run -d -p 5000:5000 --name document_manager document_manager
```

```
├── app
│   ├── document_manager.py
│   └── db_sqlite.py
│   └── initialise_db.py
│   ├── DockerFile
│   └── requirements.txt
└── README.md
```