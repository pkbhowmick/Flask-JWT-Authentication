# Flask Api for storing face embeddings in mongodb

# For model : 
- https://drive.google.com/drive/folders/1pwQ3H4aJ8a6yyJHZkTwtjcL4wYWQb7bn

# For checking with postman

### Register(POST)
- url : localhost:5000/register
- Json body : "userId" = "" , "password" = ""

### Login(POST)
- url : localhost:5000/login
- Basic auth : give your registered username and password
- A token generated following successful login

### Storing face embeddings(POST)
- url : localhost:5000/faceid
- json body: "userId": ""
- In param set token value
If everything goes righ, you'll get "Storing face embeddings successful" message.


