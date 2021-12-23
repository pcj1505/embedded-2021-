import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
 
 
nomask_dir = r'C:\yoo_dev\git\recog_mask2\img\without_mask'
mask_dir = r'C:\yoo_dev\git\recog_mask2\img\with_mask'
 
nomask_list = os.listdir(nomask_dir)
mask_list = os.listdir(mask_dir)
 
#total = len(nomask_list) + len(mask_list) 
 
x=[]
y=[]
num=1
label=0

# nomask file 0
for file in nomask_list:
    img=load_img(nomask_dir+'/'+file, target_size=(64, 64))
    img_array=img_to_array(img)
    #img_array=np.expand_dims(img_array, axis=0)
    img_array=preprocess_input(img_array)
    
    img_label=[]
    
    img_label.append(label)
    x.append(img_array)
    y.append(img_label)
    num+=1
    
label+=1
# mask file 1
for file in mask_list:
    img=load_img(mask_dir+'/'+file, target_size=(64, 64))
    img_array=img_to_array(img)
    #img_array=np.expand_dims(img_array, axis=0)
    img_array=preprocess_input(img_array)
    
    img_label=[]
    
    img_label.append(label)
    x.append(img_array)
    y.append(img_label)
    num+=1

x=np.array(x)
y=np.array(y)

 
X_train, X_test, Y_train, Y_test=train_test_split(x, y, test_size=0.2)
 
image_data=(X_train, X_test, Y_train, Y_test)
np.save(r'C:\yoo_dev\git\recog_mask2\img\dataset.npy',image_data)

print(x.shape)
print(y.shape)
print(x[0])