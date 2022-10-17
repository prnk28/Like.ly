
# coding: utf-8

# the following cell imports the json with all of our data, and counts the occurences of the tags obtained from the Microsoft Computer Vision API.

# In[19]:
import numpy as np
from collections import Counter
import json
from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error


np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)

with open('NEWDATA.json') as json_data:
    d = json.load(json_data)

json_size = len(d)


import datetime

follow_ratios = []
followers = []
days_since_posting = []
meanLikes = []
likes = []
created_time = []
tags = []

for i in range(len(d)):
    follow_ratios.append(d[i]['follow_ratio'])
    temp_followers = int(d[i]['follows']/d[i]['follow_ratio'])
    # followers = following / follow_ratio
    followers.append(temp_followers)
    days_since_posting.append('days_since_posting')
    meanLikes.append(d[i]['meanLikes'])
    likes.append(d[i]['likes'])
    temp_time = d[i]['created_time']
    postTimeFinal=(datetime.datetime.fromtimestamp(int(temp_time)))
    h = postTimeFinal.hour + postTimeFinal.minute / 60. + postTimeFinal.second / 3600.
    created_time.append(h)
    temp_string = "".join(d[i]['tags'][j] + " " for j in range(len(d[i]['tags'])))
    tags.append(temp_string)

data = [follow_ratios, followers, meanLikes, created_time, likes]
words = 10
vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = words)

train_data_features = vectorizer.fit_transform(tags)
train_data_features = train_data_features.toarray()
data = np.transpose((np.array(data)))


data = np.concatenate((train_data_features, data), axis=1)
# Now we have a vector of features

X = data[:, :-1]
y = data[:, words + 4]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

X_poly = X_train
y_poly = y_train
X_test_poly = X_test
y_test_poly = y_test

X_svr = X_train
y_svr = y_train
X_test_svr = X_test
y_test_svr = y_test

# Linear Regression
regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)


# Polynomial Regression

poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X_poly)
X_test_poly = poly.fit_transform(X_test_poly)

regressor_poly = LinearRegression()
regressor_poly.fit(X_poly, y_poly)

y_pred_poly = regressor_poly.predict(X_test_poly)

# Standard Vector Regression

# First we must do feature scaling, bc the sklearn library does not do it for us
sc_X = StandardScaler()
X_svr = sc_X.fit_transform(X_svr)
X_test_svr = sc_X.transform(X_test_svr)
sc_y = StandardScaler()
y_svr = sc_y.fit_transform(y_svr)

regressor = SVR(kernel = 'rbf')
regressor.fit(X_svr, y_svr)

y_pred_svr = regressor.predict(X_test_svr)

y_pred_svr = sc_y.inverse_transform(y_pred_svr)
X_test_svr = sc_X.inverse_transform(X_test_svr)


# Analyzing the results of our algorithms, there's probably some way to do this in sklearn

pctError = []
diff = []

pctError_poly = []
diff_poly = []

pctError_svr = []
diff_svr = []

zerocount = 0

for i in range(len(y_pred)):
    temp_diff = float(abs(int(y_pred[i] - y_test[i])))
    temp_diff_poly = float(abs(int(y_pred_poly[i] - y_test[i])))
    temp_diff_svr = float(abs(int(y_pred_svr[i] - y_test[i])))
    if (y_test[i] != 0):
        temp_pct = temp_diff / float(y_test[i]) * 100
        pctError.append(temp_pct)

        temp_pct_poly = temp_diff_poly / float(y_test[i]) * 100
        pctError_poly.append(temp_pct_poly)

        temp_pct_svr = temp_diff_svr / float(y_test[i]) * 100
        pctError_svr.append(temp_pct_svr)
            #print temp_pct
    diff.append(temp_diff)
    diff_poly.append(temp_diff_poly)
    diff_svr.append(temp_diff_svr)

errorLinear = mean_squared_error(y_true=y_test, y_pred=y_pred, multioutput='uniform_average')
errorPoly = mean_squared_error(y_test, y_pred_poly)
errorSVR = mean_squared_error(y_test, y_pred_svr)

print ("Linear Regression: ")
print ("Error: ", errorLinear)
print ("Difference: ", sum(diff)/float(len(diff)))
print ("Pct Error: ", sum(pctError)/float(len(pctError)))

print (" ")

print ("Polynomial Regression: ")
print ("Error: ", errorPoly)
print ("Difference: ", sum(diff_poly)/float(len(diff_poly)))
print ("Pct Error: ", sum(pctError_poly)/float(len(pctError_poly)))

print (" ")

print ("SVR: ")
print ("Error: ", errorSVR)
print ("Difference: ", sum(diff_svr)/float(len(diff_svr)))
print ("Pct Error: ", sum(pctError_svr)/float(len(pctError_svr)))
#
# print zerocount
