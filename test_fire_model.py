import tensorflow as tf
import numpy as np
import cv2

# Load model
model = tf.keras.models.load_model('fire_model.keras')

# Path to your test image

IMG_SIZE = 96

fireImage_path = "fire_dataset/fire_images/fire.101.png"
CleanImage_path = "fire_dataset/non_fire_images/non_fire.33.png"

# load + preprocess image

img = cv2.imread(CleanImage_path) # Change between the fire image and the clean image
img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
img = img.astype('float32') / 255.0
img = np.expand_dims(img, axis=0)

# Predict
prediction = model.predict(img)[0][0]
confidence = float(prediction)

# Result

if confidence >= 0.5:
   print(f'Fire detected! ({(1 - confidence):.2f} confidence)')
else:
   print(f'No fire ({confidence:.2f}) confidence')