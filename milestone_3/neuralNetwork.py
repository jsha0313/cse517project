from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

import os
import sys

try:
    import pandas as pd
except ImportError:
    pass

def validate_cmdline_args(nargs, msg):
    if len(sys.argv) < nargs:
        print(msg)
        sys.exit(1)
validate_cmdline_args(3,'Usage: python neuralNetwork.py <DATASET_PATH_RED> <DATASET_PATH_WHITE>')
DATASET_PATH_RED = sys.argv[1]
DATASET_PATH_WHITE = sys.argv[2]

data_features = ["fa","va","ca","rs","ch","fsd","tsd","dens","pH","sulp","alcohol","eval"]
data_red = pd.read_csv(DATASET_PATH_RED,names=data_features)
data_white = pd.read_csv(DATASET_PATH_RED,names=data_features)

                            ## Red Wine ##
print('-------------Red Wine Evaluation-------------')
np.random.seed(None)

x_train = data_red.sample(frac=0.7, random_state=None)
x_test = data_red.drop(x_train.index)

y_train = x_train.pop("eval")
y_test = x_test.pop("eval")

train = (x_train, y_train)
test = (x_test, y_test)

dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))

train = dataset.shuffle(1000).batch(128).repeat().make_one_shot_iterator().get_next()

feature_columns = [tf.feature_column.numeric_column(key="fa"),
                   tf.feature_column.numeric_column(key="va"),
                   tf.feature_column.numeric_column(key="ca"),
                   tf.feature_column.numeric_column(key="rs"),
                   tf.feature_column.numeric_column(key="ch"),
                   tf.feature_column.numeric_column(key="fsd"),
                   tf.feature_column.numeric_column(key="tsd"),
                   tf.feature_column.numeric_column(key="dens"),
                   tf.feature_column.numeric_column(key="pH"),
                   tf.feature_column.numeric_column(key="sulp"),
                   tf.feature_column.numeric_column(key="alcohol"),
                   tf.feature_column.numeric_column(key="eval"),
                   ]

model = tf.estimator.LinearRegressor(feature_columns=data_features)
#model.train(input_fn=train, steps=1000)
