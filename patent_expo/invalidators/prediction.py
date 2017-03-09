import csv
import numpy as np
import pandas as pd
import MySQLdb, pickle

from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn import cross_validation
from sqlalchemy import create_engine

# Connecting to the db
host_db = "cal-patent-lab.chhaitskv8dz.us-west-2.rds.amazonaws.com"
username = ***REMOVED***
password = ***REMOVED***
db = ***REMOVED***

engine = create_engine("mysql://{}:{}@{}/{}".format(
    username, password, host_db, db))
connection = engine.connect()
patents_decision = pd.read_sql("SELECT patent_id, invalidated, CAST( claims_text AS CHAR ) FROM patents_decision", engine)

patents_data = patents_decision[patents_decision["invalidated"].isin([0, 1])]
X = patents_data['CAST( claims_text AS CHAR )'].as_matrix()
y = patents_data['invalidated'].as_matrix()

# Removing element with no text
index_to_remove= []
for i in range(len(X)):
    if X[i] == None:
        index_to_remove.append(i)
        
X = np.delete(X, index_to_remove)
y = np.delete(y, index_to_remove)

X_train, X_test, y_train, y_test = cross_validation.train_test_split(
    X, y, test_size=0.2, random_state=20)


patents_data = patents_decision[patents_decision["invalidated"].isin([0, 1])]
X = patents_data['CAST( claims_text AS CHAR )'].as_matrix()
y = patents_data['invalidated'].as_matrix()

# Removing element with no text
index_to_remove= []
for i in range(len(X)):
    if X[i] == None:
        index_to_remove.append(i)
        
X = np.delete(X, index_to_remove)
y = np.delete(y, index_to_remove)

X_train, X_test, y_train, y_test = cross_validation.train_test_split(
    X, y, test_size=0.2, random_state=20)


# this normalizes word frequency based on use in each patent vs. all patents

tfidf = TfidfVectorizer()
tfidf.fit(X)
X_train = tfidf.transform(X_train)
X_test = tfidf.transform(X_test)

svc_class = LinearSVC(C=1)
model = svc_class.fit(X_train, y_train)
with open('model.pickle', 'w') as f:  # Python 3: open(..., 'wb')
    pickle.dump([model,tfidf], f)
    


