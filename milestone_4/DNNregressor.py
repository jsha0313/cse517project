from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

import os
import sys
import collections
try:
    import pandas as pd
except ImportError:
    pass

# disable warning messages:
tf.logging.set_verbosity(tf.logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# functions:
def validate_cmdline_args(nargs, msg):
    if len(sys.argv) < nargs:
        print(msg)
        sys.exit(1)

def dataset(y_name="eval", train_fraction=0.7, dataset_path=""):
  path = dataset_path

  def decode_line(line):
    items = tf.decode_csv(line, list(defaults.values()))
    pairs = zip(defaults.keys(), items)
    features_dict = dict(pairs)
    label = features_dict.pop(y_name)
    return features_dict, label

  def in_training_set(line):
    num_buckets = 1000000
    bucket_id = tf.string_to_hash_bucket_fast(line, num_buckets)
    return bucket_id < int(train_fraction * num_buckets)

  def in_test_set(line):
    return ~in_training_set(line)

  base_dataset = (tf.data.TextLineDataset(path))
  train = (base_dataset.filter(in_training_set).map(decode_line).cache())
  test = (base_dataset.filter(in_test_set).cache().map(decode_line))

  return train, test

def dataset_for_infile(y_name="eval", train_path="", test_path=""):
  tr_path = train_path
  te_path = test_path

  def decode_line(line):
    items = tf.decode_csv(line, list(defaults.values()))
    pairs = zip(defaults.keys(), items)
    features_dict = dict(pairs)
    label = features_dict.pop(y_name)
    return features_dict, label

  train = (tf.data.TextLineDataset(tr_path)).map(decode_line).cache()
  test = (tf.data.TextLineDataset(te_path)).cache().map(decode_line)
  # train = (train_base_dataset.filter(True).map(decode_line).cache())
  # test = (test_base_dataset.filter(True).cache().map(decode_line))

  return train, test

def input_train():
    return (train.shuffle(1000).batch(128).repeat()
		.make_one_shot_iterator().get_next())

def input_test():
    return (test.shuffle(1000).batch(128)
		.make_one_shot_iterator().get_next())

def input_simple_train():
    return train

def input_simple_test():
    return test

def simple_split(dataset_path=""):
  path = dataset_path
  data = pd.read_csv(path)
  train_x, test_x, train_y, test_y = train_test_split(data[data_features[:7]],data[data_features[8]], train_size=0.7)
  return train_x, test_x, train_y, test_y

def to_thousands(features, labels):
    return features, labels / 1000

sess = tf.Session()

defaults = collections.OrderedDict([
    ("f1", [0.0]),
    ("f2", [0.0]),
    ("f3", [0.0]),
    ("f4", [0.0]),
    ("f5", [0.0]),
    ("f6", [0.0]),
    ("f7", [0.0]),
    ("f8", [0.0]),
    ("eval", [0])
])

feature_columns = [tf.feature_column.numeric_column(key="f1"),
                   tf.feature_column.numeric_column(key="f2"),
                   tf.feature_column.numeric_column(key="f3"),
                   tf.feature_column.numeric_column(key="f4"),
                   tf.feature_column.numeric_column(key="f5"),
                   tf.feature_column.numeric_column(key="f6"),
                   tf.feature_column.numeric_column(key="f7"),
                   tf.feature_column.numeric_column(key="f8"),
                   ]
types = collections.OrderedDict((key, type(value[0]))
                                for key, value in defaults.items())

run_infile = False

if(sys.argv[1]=="true" or sys.argv[1]=="True"):
    run_infile = True

# our code runs here:
validate_cmdline_args(2,'Usage: python neuralNetwork.py <RUN INFILE BOOLEAN> <DATASET_PATH>')
hidden_layers = [4, 4, 4, 4, 4]

if not run_infile:
  # delete header line:
  with open(sys.argv[2],'r') as f:
      with open("dnn_"+sys.argv[2],'w') as f1:
          f.next() # skip header line
          for line in f:
              f1.write(line)

  (train, test) = dataset(dataset_path="dnn_"+sys.argv[2])

  train = train.map(to_thousands)
  test = test.map(to_thousands)

  iterator = test.make_one_shot_iterator()
  next_element = iterator.get_next()

  original_values = []
  predict_values = []

  for i in range(0,461):
    value = sess.run(next_element)
    original_values.append(int(1000*value[1]))

  print(len(original_values))

  for i in range(0,len(original_values)):
    print("No. "+str(i)+": "+str(original_values[i]))

  model = tf.estimator.DNNRegressor(hidden_units=hidden_layers, feature_columns=feature_columns, activation_fn=tf.nn.sigmoid)
  model.train(input_fn=input_train, steps=1000)
  eval_result = model.evaluate(input_fn=input_test)
  # model_predict = model.predict(input_fn=input_test)

  y = list(model.predict(input_fn=input_test))
  # for i in range(0,len(y)):
  #   print(y[i].get("predictions")[0])

  for i in range(0,len(y)):
    predict_values.append(int(round(1000*y[i].get("predictions")[0])))

  prediction_accuracy = 0

  for i in range(0,len(original_values)):
    if original_values[i]==predict_values[i]:
      prediction_accuracy = prediction_accuracy + 1

  print("\n" + 30 * "*" + "DNN RESULTS" + 30 * "*")
  print("Prediction Accuracy: "+str(prediction_accuracy/len(original_values)))
  print("loss: "+str(eval_result["loss"]))
  print("average loss: "+str(eval_result["average_loss"]))
  # Convert MSE to Root Mean Square Error (RMSE).
  print("RMS error for the test set: {:.0f}".format(1000 * eval_result["average_loss"]**0.5))
  print(71 * "*" + "\n")

else:
  temp_array_train = sys.argv[2].split("/")
  TRAIN_PATH = ""

  for i in range(1,len(temp_array_train)-1):
    TRAIN_PATH = TRAIN_PATH +"/"+temp_array_train[i]

  if TRAIN_PATH!="":
    TRAIN_PATH = TRAIN_PATH + "/dnn_" + temp_array_train[len(temp_array_train)-1]
  else:
    TRAIN_PATH = "dnn_" + temp_array_train[len(temp_array_train)-1]

  temp_array_test = sys.argv[3].split("/")
  TEST_PATH = ""

  for i in range(1,len(temp_array_test)-1):
    TEST_PATH = TEST_PATH +"/"+temp_array_test[i]

  if TEST_PATH!="":
    TEST_PATH = TEST_PATH + "/dnn_" + temp_array_test[len(temp_array_test)-1]
  else:
    TEST_PATH = "dnn_" + temp_array_test[len(temp_array_test)-1]

  # delete header line:
  with open(sys.argv[2],'r') as f:
      with open(TRAIN_PATH,'w') as f1:
          f.next() # skip header line
          for line in f:
              f1.write(line)

  with open(sys.argv[3],'r') as f:
      with open(TEST_PATH,'w') as f1:
          f.next() # skip header line
          for line in f:
              f1.write(line)

  

  (train, test) = dataset_for_infile(train_path=TRAIN_PATH, test_path=TEST_PATH)

  train = train.map(to_thousands)
  test = test.map(to_thousands)

  iterator = test.make_one_shot_iterator()
  next_element = iterator.get_next()

  original_values = []
  predict_values = []

  data_temp = pd.read_csv(TEST_PATH)

  endDigit = len(data_temp)

  for i in range(0,endDigit):
    value = sess.run(next_element)
    original_values.append(int(1000*value[1]))

  model = tf.estimator.DNNRegressor(hidden_units=hidden_layers, feature_columns=feature_columns, activation_fn=tf.nn.sigmoid)
  model.train(input_fn=input_train, steps=1000)
  y = list(model.predict(input_fn=input_test))
  # for i in range(0,len(y)):
  #   print(y[i].get("predictions")[0])

  for i in range(0,len(y)):
    predict_values.append(int(round(1000*y[i].get("predictions")[0])))

  prediction_accuracy = 0

  for i in range(0,len(original_values)):
    if original_values[i]==predict_values[i]:
      prediction_accuracy = prediction_accuracy + 1

  print(prediction_accuracy/len(original_values))