# -*- coding: utf-8 -*-
"""IMDB_Bidirectional_word2vec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oT--fjG78yxaAOn7GRlSPgKBOsr1F8S5
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import string
from nltk.corpus import stopwords

from google.colab import drive
drive.mount('/content/drive')

path='/content/drive/MyDrive/IMDB_Dataset.csv'
data=pd.read_csv(path)

data.shape

df=data.iloc[:5000]
# df = data.iloc[:10000]
df['review'][1]
df.shape

df['sentiment'].value_counts()

"""## Preprocessing of data"""

df.isnull().sum()

df.duplicated().sum()

df.drop_duplicates(inplace=True)

df.duplicated().sum()

df.shape

import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import string

# Define the text preprocessing pipeline
def preprocess_text(text):
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stopwords_list = stopwords.words('english')
    filtered_tokens = [token for token in tokens if token not in stopwords_list]
    
    # Lowercase the tokens
    lowercase_tokens = [token.lower() for token in filtered_tokens]
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    no_punct_tokens = [token.translate(translator) for token in lowercase_tokens]
    
    # Remove empty tokens
    final_tokens = [token for token in no_punct_tokens if token]
    
    # Join the tokens back into a single string
    preprocessed_text = ' '.join(final_tokens)
    
    return preprocessed_text

df['review']= df['review'].apply(preprocess_text)

X= df['review']
print(X.shape)
y = df['sentiment']

print(X)

print(y)

from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
y = encoder.fit_transform(y)

print(y)

y = y.astype('float32')

"""## Word2vec

"""

from sklearn.model_selection import train_test_split

# Split the data into train and test sets
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Split the train set into train and validation sets
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.25, random_state=0)

x_train

!pip install --upgrade tensorflow
!pip install --upgrade keras

!pip install tensorflow==2.5.0

import gensim.downloader as api
# Load Word2Vec model
w2v_model = api.load("word2vec-google-news-300")

import numpy as np
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional, Dropout
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
from gensim.models import KeyedVectors
import gensim.downloader as api
import tensorflow as tf

# Load the IMDB dataset
max_features = 500
maxlen = 100
(X_train, y_train), (X_test, y_test) = imdb.load_data(num_words=max_features)
X_train= X_train[1:5000]
y_train= y_train[1:5000]
# Preprocess the input data
X_train = pad_sequences(X_train, maxlen=maxlen, padding='post')
X_test = pad_sequences(X_test, maxlen=maxlen, padding='post')

# # Load Word2Vec model
# w2v_model = api.load("word2vec-google-news-300")

# Define the embedding matrix
embedding_dim = 300
embedding_matrix = np.zeros((max_features, embedding_dim))
for word, i in imdb.get_word_index().items():
    if i < max_features:
        try:
            embedding_vector = w2v_model.get_vector(word)
            embedding_matrix[i] = embedding_vector
        except KeyError:
            pass

# Define the model
model = Sequential()
model.add(Embedding(max_features, embedding_dim, input_length=maxlen, weights=[embedding_matrix], trainable=False))
model.add(Bidirectional(LSTM(128, return_sequences=True)))
model.add(Dropout(0.2))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Fit the model
batch_size = 32
epochs = 1

# Decorate the make_test_function method with the do_not_convert decorator
@tf.autograph.experimental.do_not_convert
def test_function(self, step_function, batch_size=None, verbose=0, steps=None):
    return step_function(self.distribute_strategy, self.inputs, self.targets, sample_weights=self.sample_weights, batch_size=batch_size, verbose=verbose, steps=steps)

# model._test_loop = tf.function(model._test_loop, experimental_relax_shapes=True)
# model.make_test_function = test_function.__get__(model)
model.test_step = tf.function(model.test_step)

model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=batch_size, epochs=epochs, verbose=2)

y_pred = np.argmax(model.predict(x_test), axis=-1)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
acc = accuracy_score(y_test, y_pred)
print("Test Accuracy: ", acc)
# precision score
precision = precision_score(y_test, y_pred)
print('Precision:', precision)

# recall score
recall = recall_score(y_test, y_pred)
print('Recall:', recall)

# F1 score
f1 = f1_score(y_test, y_pred)
print('F1 score:', f1)

# confusion matrix
confusion_mat = confusion_matrix(y_test, y_pred)
print('Confusion matrix:\n', confusion_mat)