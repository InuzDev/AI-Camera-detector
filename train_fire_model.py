import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib as plt

# Config
IMG_SIZE = 96
BATCH_SIZE = 16
EPOCHS = 256

# Dataset prep
datagen = ImageDataGenerator(
   rescale=1./255,
   validation_split=0.2,
   rotation_range=15,
   width_shift_range=0.1,
   height_shift_range=0.1,
   shear_range=0.1,
   zoom_range=0.1,
   horizontal_flip=True
)

train_data = datagen.flow_from_directory(
   'fire_dataset',
   target_size=(IMG_SIZE, IMG_SIZE),
   batch_size=BATCH_SIZE,
   class_mode='binary',
   subset="validation"
)

val_data = datagen.flow_from_directory(
   'fire_dataset',
   target_size=(IMG_SIZE, IMG_SIZE),
   batch_size=BATCH_SIZE,
   class_mode='binary',
   subset='validation'
)

# CNN model
model = models.Sequential([
   layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
   layers.Conv2D(16, (3, 3), activation='relu'),
   layers.MaxPooling2D(2, 2),
   layers.Conv2D(32, (3, 3), activation='relu'),
   layers.MaxPooling2D(2, 2),
   layers.Flatten(),
   layers.Dense(32, activation='relu'),
   layers.Dropout(0.1),
   layers.Dense(64, activation='relu'),
   layers.Dense(1, activation="sigmoid")
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Train
history = model.fit(train_data, validation_data=val_data, epochs=EPOCHS)

# Save model
SavedModel = model.save('fire_model.keras')

checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
   "fire_model_best.keras", save_best_only=True
)

model.fit(..., callbacks=[checkpoint_cb])

print(train_data.class_indices) # Tells how the images are labeled internally

# Convert to TFLite

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.default]
tflite_model = converter.convert()

with open('fire_model.tflite', 'wb') as f:
  f.write(tflite_model)

print("Model saved as fire_model.h5 and fire_model.tflite")