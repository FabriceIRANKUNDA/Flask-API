from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
from datetime import datetime
from pymongo import MongoClient
import urllib.parse
import cloudinary
import cloudinary.uploader
import dns
import functools
import time

from predictor import return_prediction

login = 'fabu'
password = urllib.parse.quote("sensorNode@mongodb")
host = '@cluster0.v7qp1.mongodb.net'
db = 'sensorNodesample'
uri = f'mongodb+srv://{login}:{password}{host}/{db}'
t_url = None
t_res = None



app = Flask(__name__)
CORS(app)
mongo = pymongo.MongoClient(uri)
db = mongo['sensorNodesample']
col = db['images']


def autoreconnect(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        max_retry = 3
        attempts = 0
        while True:
            try:
                return f(*args, **kwargs)
            except pymongo.errors.AutoReconnect as e:
                attempts += 1
                if attempts >= max_retry:
                    raise e
                time.sleep(0.3)
    return wrapper


def allowed_image(filename):
    allowed_ext = ["JPG", "PNG", "JPEG"]

    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in allowed_ext:
        return True
    else:
        return False

@app.route('/upload-image', methods=["GET", "POST"])
@autoreconnect
def upload_image():
    image = request.files["image"]
    try:
        if request.files:
            content = image.stream.read()
            if content != b'':
                cloudinary.config(
                cloud_name = "doi0bys97",
                api_key = "892939279365239",
                api_secret = "WMOPFxJLPP0DEVq8wR4e5afC34o")

                result_cloud = cloudinary.uploader.upload(content)
                global t_url 
                t_url = result_cloud.get("url")
                global t_res
                
                if image.filename == "":
                    return jsonify({'status': 'fail', 'message': 'Image must have name.'})
                if not allowed_image(image.filename):
                    return jsonify({'status': 'fail', 'message': 'Unsupported image. allowed images: JPG, PNG and JPEG'})
                else:
                    t_res = return_prediction(content, image.filename)
                    col.insert_one({"url": t_url, "prediction": t_res, "createdAt": datetime.now()})
                    return jsonify({'status': 'success', 'message': 'Image predicted successfully', 'predict': t_res, 'image_url': t_url}), 200
            else:
                col.insert_one({"url": t_url, "prediction": t_res, "createdAt": datetime.now()})
                return jsonify({'status': 'success', 'message': 'Image predicted successfully', 'predict': t_res, 'image_url': t_url}), 200
    except FileNotFoundError:
        pass
    else:
        image.close()

@app.route('/images', methods=["GET"])
@autoreconnect
def get_all_images():
    result = []
    try:
        for img in col.find().sort('createdAt', pymongo.DESCENDING):
            result.append({'url': img['url'], 'pred': img['prediction'], 'createdAt': img['createdAt']})
        return jsonify({'status': 'success', 'message': 'Image predicted successfully', 'data': result, }), 200
    finally:
        pass
    

if __name__ == '__main__':
    app.run()
