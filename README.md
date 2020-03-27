# Flask Api for storing face embeddings in mongodb

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


