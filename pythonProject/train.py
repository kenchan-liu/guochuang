import argparse
from tensorflow import keras
import tensorflow as tf
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
# from keras.utils import multi_gpu_model
from config import patience, n_epochs, num_train_samples, num_valid_samples, batch_size
from data_generator import train_gen, valid_gen
from model import build_model

if __name__ =='__main__':

    checkpoint_models_path = 'models/'

    #Callbacks
    tensor_board = keras.callbacks.TensorBoard(log_dir='.logs', histogram_freq=0, write_graph=True, write_images=True)
    model_names = checkpoint_models_path + 'model.{epoch:02d}-{val_loss:4f}.hdf5'
    model_checkpoint = ModelCheckpoint(model_names, monitor='val_loss', verbose=1, save_best_only=True)
    early_stop = EarlyStopping('val_loss', patience=patience)
    reduce_lr = ReduceLROnPlateau('val_loss', factor=0.1, patience=int(patience / 5), verbose=1)

    class MyCallback(keras.callbacks.Callback):
        def __init__(self,model):
            keras.callbacks.Callback.__init__(self)
            self.model_to_save=model

        def on_epoch_end(self,epoch,logs=None):
            fmt=checkpoint_models_path+'model.%2d-%.4f.hdf5'
            self.model_to_save.save(fmt % (epoch,logs['val_loss']))


    new_model = build_model()

    adam=keras.optimizers.Adam(lr=5e-5)
    new_model.compile(optimizer=adam, loss='categorical_crossentropy', metrics=['accuracy'])

    print(new_model.summary)

    #Final callbacks
    callbacks = [tensor_board,model_checkpoint,early_stop,reduce_lr]

    #Start Fine-tuning
    new_model.fit_generator(train_gen(),
                            steps_per_epoch = num_train_samples//batch_size,
                            validation_data=train_gen(),
                            validation_steps=num_valid_samples//batch_size,
                            epochs=n_epochs,
                            verbose=1,
                            callbacks=callbacks,
                            use_multiprocessing=False,
                            )