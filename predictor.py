import numpy as np
from tensorflow.keras.preprocessing import image
import cv2
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

def return_prediction(content, file_name):
    classes = ["Average", "Bad", "Excellent", "Good", "Not_maize", "Worst"]
    model_path = './model/best_model_VGG_last.h5'
    frame = cv2.imdecode(np.fromstring(content, np.uint8), cv2.IMREAD_COLOR)
    cv2.imwrite("./image/" + file_name, frame)

    img_sent = image.load_img('./image/' + file_name, target_size=(245, 245, 3))
    model = load_model(model_path)
    # my_image = image.img_to_array(frame)
    my_image_shape = np.expand_dims(img_sent, axis=0)
    print("IMAGE HHHHHHHHHHHHHH", my_image_shape.shape)
    result = model.predict(my_image_shape)
    os.remove("./image/" + file_name)
    predicted_class = ""
    
    for index, res in enumerate(result[0]):
        if res > 0.5:
            predicted_class = classes[index]
            break

    return predicted_class
