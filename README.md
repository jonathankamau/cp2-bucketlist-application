## Checkpoint 2: Bucket List API application



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
         
    The API server is accessible on `http://127.0.0.1:5000/` 
### Sample API Use Case
Access the endpoints using your preferred client e.g Postman

		   
