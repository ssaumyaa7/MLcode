from keras.applications import VGG16
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint, EarlyStopping

#Loads the VGG16 model 
model = VGG16(weights = 'imagenet', include_top = False, input_shape = (244, 244, 3))

for layer in model.layers:
    layer.trainable = False
    
# Let's print our layers 
for (i,layer) in enumerate(model.layers):
    print(str(i) + " "+ layer.__class__.__name__, layer.trainable)
    
def Top(bottom_model, num_classes, D=256):
    head = bottom_model.output
    head = Flatten(name = "flatten")(head)
    head = Dense(D, activation = "relu")(head)
    head = Dropout(0.3)(head)
    head = Dense(num_classes, activation = "softmax")(head)
    return head

top = Top(model, 4)
modelnew = Model(inputs=model.input, outputs=top)

print(modelnew.summary())

training = 'C:/MLOPS/transfer_learninig_vgg16/images/train'
testing = 'C:/MLOPS/transfer_learninig_vgg16/images/test'

train_data = ImageDataGenerator( rescale=1./255, rotation_range=20, width_shift_range=0.2, height_shift_range=0.2,
horizontal_flip=True, fill_mode='nearest')
 
test_data = ImageDataGenerator(rescale=1./255)
train_batchsize = 6
val_batchsize = 4
 
train_gen = train_data.flow_from_directory(training, target_size=(244, 244), batch_size=train_batchsize,
                                              class_mode='categorical')
 
test_gen = test_data.flow_from_directory(testing, target_size=(244,244), batch_size=val_batchsize,
class_mode='categorical', shuffle=False)                   
checkpoint = ModelCheckpoint("actor.h5", monitor="val_loss", mode="min", save_best_only = True,
                             verbose=1)
earlystop = EarlyStopping(monitor = 'val_loss', min_delta = 0, patience = 3, verbose = 1, restore_best_weights = True)
callbacks = [earlystop, checkpoint]

modelnew.compile(loss = 'categorical_crossentropy', optimizer = RMSprop(lr = 0.001),
              metrics = ['accuracy'])

train_img = 167
test_img = 37
epochs = 3
batch_size = 1

history = modelnew.fit_generator(train_gen, steps_per_epoch = train_img // batch_size, epochs = epochs,
callbacks = callbacks, validation_data = test_gen, validation_steps = test_img // batch_size)

modelnew.save("actor.h5")
