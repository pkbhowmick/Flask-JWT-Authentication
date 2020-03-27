from flask import Flask, jsonify, request
from flask_restful import Resource,Api, request
from flask_pymongo import PyMongo
###for face embeddings
from PIL import Image
from keras.models import load_model
import mtcnn
from numpy import asarray
from mtcnn.mtcnn import MTCNN
from matplotlib import pyplot
from os import listdir
from os.path import isdir
from numpy import savez_compressed
from numpy import load
from numpy import expand_dims
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
from random import choice
###for jwt authentication
from flask import make_response
import jwt
import datetime
from functools import wraps


app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME'] = 'facedb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/facedb'
app.config['SECRET_KEY'] = 'secretkey'

app.url_map.strict_slashes = False

mongo = PyMongo(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({"message" : "Token is missing"}) , 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid'}) , 403
        
        return f(*args, **kwargs)
    return decorated


def get_embeddings(filename, required_size=(160, 160)):
    # load image from file
    image = Image.open(filename)
    # convert to RGB, if needed
    image = image.convert('RGB')
    # convert to array
    pixels = asarray(image)
    # create the detector, using default weights
    detector = MTCNN()
    # detect faces in the image
    results = detector.detect_faces(pixels)
    # extract the bounding box from the first face
    x1, y1, width, height = results[0]['box']
    # bug fix
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = asarray(image)
    X = list()
    X.extend(face_array)
    face_pixels = asarray(X)
    model = load_model('facenet_keras.h5')
    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    # transform face into one sample
    samples = expand_dims(face_pixels, axis=0)
    # make prediction to get embedding
    yhat = model.predict(samples)
    return yhat[0]


@app.route('/register',methods=['POST'])
def register():
    userId = request.json['userId']
    password = request.json['password']
    face = mongo.db.FACE
    user = face.find_one({'userId' : userId})
    if user:
        return jsonify({'message' : 'User already exists'})
    else:
        face.insert({"userId" : userId,"password" : password , "faceEmbeddings" : None})
        return jsonify({'message' : 'User created successfully'})




@app.route('/login',methods=['GET','POST'])
def login():
    auth = request.authorization
    face = mongo.db.FACE
    user = face.find_one({'userId' : auth.username})
    if auth and user and auth.password == user['password']:
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@app.route('/faceid',methods=['GET','POST'])
@token_required
def post():
    face = mongo.db.FACE
    userId = request.json["userId"]
    user = face.find_one({'userId' : userId})
    if user['faceEmbeddings'] == None:
        embeddings = get_embeddings("picture.jpg")
        embeddings = embeddings.tolist()
        user['faceEmbeddings'] = embeddings
        return jsonify({"message" : "Registration successful"})
    else:
        return jsonify({"message" : "Your Face Embeddings already existed"})


#api.add_resource(FaceById,"/faceid/<string:userId>")

if __name__ == '__main__':
    app.run(debug=True)
