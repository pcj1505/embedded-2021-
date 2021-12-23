import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Flatten, BatchNormalization
from tensorflow.keras.applications.resnet50 import ResNet50

# load dataset
X_train,X_test,Y_train,Y_test=np.load(r'C:\yoo_dev\git\recog_mask2\img\dataset.npy',allow_pickle=True)

## 
base_model = ResNet50(input_shape=(64, 64, 3), weights='imagenet', include_top=False)
base_model.trainable = False
base_model.summary()
print("Number of layers in the base model: ", len(base_model.layers))
 
flatten_layer = Flatten()
dense_layer1 = Dense(128, activation='relu')
bn_layer1 = BatchNormalization()
dense_layer2 = Dense(1, activation=tf.nn.sigmoid)
 
model = Sequential([
        base_model,
        flatten_layer,
        dense_layer1,
        bn_layer1,
        dense_layer2,
        ])
 
base_learning_rate = 0.001
model.compile(optimizer=tf.keras.optimizers.Adam(lr=base_learning_rate),
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.summary()

# model training
model.fit(X_train, Y_train, batch_size=40, epochs=10, verbose=1)

# model test
test_loss, test_acc = model.evaluate(X_test, Y_test, verbose=1)
print('\n테스트 정확도 : %.3f' % (test_acc*100)+'%')

# save model
model.save("CNN_model.h5")
print("Save model Complete")

