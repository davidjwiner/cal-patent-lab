import pickle
import numpy as np


def predict_probability(text, mode='denials'):
    """
    Get the probability that a PTAB case concerning a patent 
    will be denied.
    
    Keyword arguments:
    text -- Text of the patent (string)
    mode -- Predict invalidation or denials (string)
    """
    assert mode in ['denials', 'invalidation']
    with open('./pickles/{}_model.pkl'.format(mode), 'rb') as model_file:
        model = pickle.load(model_file)

    with open('./pickles/{}_tfidf.pkl'.format(mode), 'rb') as vectorizer_file:
        tfidf = pickle.load(vectorizer_file)
        
    text_transformed = tfidf.transform([text])
    predicted_probability = model.predict_proba(text_transformed)[0][1]
    
    return predicted_probability


def get_top_keywords(text, mode='denials', most_predictive=True):
    """
    Gets the words that are most predictive of patent denial/invalidation (or lack thereof).
    
    Keyword arguments:
    text -- Text of the patent (string)
    mode -- Predict invalidation or denials (string)
    most_predictive -- If true, function returns words from TEXT that are
                       most likely to predict denial. If false, function
                       returns words from TEXT that are least likely to
                       predict denial. (boolean)
    """
        
    with open('./pickles/{}_model.pkl'.format(mode), 'rb') as model_file:
        model = pickle.load(model_file)

    with open('./pickles/{}_tfidf.pkl'.format(mode), 'rb') as vectorizer_file:
        tfidf = pickle.load(vectorizer_file)

    text_transformed = tfidf.transform([text])
    predicted_probability = model.predict_proba(text_transformed)[0][1]
    coeffs = model.coef_
    word_labels = tfidf.get_feature_names()

    if mode == 'invalidation':
        mult = np.multiply(coeffs, text_transformed.toarray())
        if most_predictive:
            top_word_indices = np.argsort(mult)[0][-3:][::-1]
            return [word_labels[idx] for idx in top_word_indices]
        
        else:
            bottom_word_indices = np.argsort(mult)[0][:3][::-1]
            return [word_labels[idx] for idx in bottom_word_indices]
    else: # mode is 'denials'
        mult = coeffs.multiply(text_transformed)
        if most_predictive:
            top_word_indices = np.argsort(mult.todense().tolist()[0])[-3:][::-1]
            return [word_labels[idx] for idx in top_word_indices]
        
        else:
            bottom_word_indices = np.argsort(mult.todense().tolist()[0])[:3][::-1]
            return [word_labels[idx] for idx in bottom_word_indices]
