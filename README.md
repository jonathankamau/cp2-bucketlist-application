## Checkpoint 2: Bucket List API application
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e002026263b1406f842a68886b81577e)](https://www.codacy.com/app/jonathankamau/cp2-bucketlist-application?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jonathankamau/cp2-bucketlist-application&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/e002026263b1406f842a68886b81577e)](https://www.codacy.com/app/jonathankamau/cp2-bucketlist-application?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jonathankamau/cp2-bucketlist-application&amp;utm_campaign=Badge_Grade)
![CircleCI](https://circleci.com/gh/jonathankamau/cp2-bucketlist-application/tree/development.svg?style=shield&circle-token=51bfa19ac63ea6e9c476ed22b04b5b44f8b5e069)


This API enables the user to create bucketlist and list of items in the bucketlist. The items can be marked as `done` when completed.

#### URL endpoints

| URL Endpoint | HTTP Methods | Summary |
| -------- | ------------- | --------- |
| `/api/v1/auth/register/` | `POST`  | Register a new user|
|  `/api/v1/auth/login/` | `POST` | Login and retrieve token|
| `/api/v1/bucketlists/` | `POST` | Create a new Bucketlist |
| `/api/v1/bucketlists/` | `GET` | Retrieve all bucketlists for user |
| `/api/v1/bucketlists/?limit=2&page=1` | `GET` | Retrieve one bucketlist per page |
| `/api/v1/bucketlists/<id>/` | `GET` |  Retrieve bucket list details |
| `/api/v1/bucketlists/<id>/` | `PUT` | Update bucket list details |
| `/api/v1/bucketlists/<id>/` | `DELETE` | Delete a bucket list |
| `/api/v1/bucketlists/<id>/items/` | `POST` |  Create items in a bucket list |
| `/api/v1/bucketlists/<id>/items/<item_id>/` | `DELETE`| Delete a item in a bucket list|
| `/api/v1/bucketlists/<id>/items/<item_id>/` | `PUT`| update a bucket list item details|

### Installation
1. create a working directory

	      $ mkdir -p work-dir
	      $ cd workdir


2. clone this repo to local
    - Via SSH

          	git clone git@github.com:jonathankamau/cp2-bucketlist-application.git

    - via HTTPS

          	git clone https://github.com/jonathankamau/cp2-bucketlist-application.git
          
3. Navigate to project directory
    
    
      		$ cd cp2-bucketlist-application
      		$ git checkout development
      
4. (Recommended)Create virtual environment 


      	$ virtualenv venv-bucketlist
      	$ source bucketlist-venv/bin/activate
          
5. Set up the development environment for the project 


          $ pip install -r requirements.txt
          $ python manage.py db init 
          $ python manage.py db migrate 
          $ python manage.py db upgrade

6. run server    

       	$ python manage.py runserver 
          Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

7. Running tests

        Run the following command in order to run tests:
        $ nosetests -v

        Running tests to check coverage:
        $ nosetests --with-coverage

### APPLICATION OPERATIONS

1. Register the user

![Register](https://cloud.githubusercontent.com/assets/26286275/26498848/1e0a7b66-4239-11e7-9e91-7515869032bc.png)

2. Login the user
![Login](https://cloud.githubusercontent.com/assets/26286275/26499067/e8cca36a-4239-11e7-80ab-b07277ee5733.png)

3. Create a bucketlist
![Create A Bucketlist](https://cloud.githubusercontent.com/assets/26286275/26499805/922dba78-423c-11e7-84eb-3cc8abfd3f1f.png)

4. Get all bucketlists
![Get Bucketlists](https://cloud.githubusercontent.com/assets/26286275/26499814/98ac6728-423c-11e7-860d-63fc5de57fbe.png)

5. Get a bucketlist
![Get a bucketlist](https://cloud.githubusercontent.com/assets/26286275/26500073/595eb674-423d-11e7-8468-6900a80af5d5.png)

6. Create a bucketlist item
![Create Bucketlist Item](https://cloud.githubusercontent.com/assets/26286275/26500441/a0e81fa2-423e-11e7-9ceb-08b9c2a61cf4.png)

    The API server is accessible on `http://127.0.0.1:5000/`
    and it is also accessible online on https://jk-bucketlist.herokuapp.com
    
### Sample API Use Case
Access the endpoints using your preferred client e.g Postman

		   
