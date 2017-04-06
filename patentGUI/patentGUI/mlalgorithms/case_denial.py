import pickle
import numpy as np

def denial_probability(text):
    """
    Get the probability that a PTAB case concerning a patent 
    will be denied.
    
    Keyword arguments:
    text -- Text of the patent (string)
    """
    with open('./pickles/denials_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file, encoding='latin1')

    with open('./pickles/denials_tfidf.pkl', 'rb') as vectorizer_file:
        tfidf = pickle.load(vectorizer_file, encoding='latin1')
        
    text_transformed = tfidf.transform([text])
    denial_probability = model.predict_proba(text_transformed)[0][1]
    
    return denial_probability

def top_denial_words(text, most_predictive=True):
    """
    Gets the words that are most predictive of patent denial (or lack thereof).
    
    Keyword arguments:
    text -- Text of the patent (string)
    most_predictive -- If true, function returns words from TEXT that are
                       most likely to predict denial. If false, function
                       returns words from TEXT that are least likely to
                       predict denial. (boolean)
    """
        
    with open('./pickles/denials_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file, encoding='latin1')

    with open('./pickles/denials_tfidf.pkl', 'rb') as vectorizer_file:
        tfidf = pickle.load(vectorizer_file, encoding='latin1')
        
    text_transformed = tfidf.transform([text])
    denial_probability = model.predict_proba(text_transformed)[0][1]
    
    coeffs = model.coef_
    mult = coeffs.multiply(text_transformed)
    word_labels = tfidf.get_feature_names()
    
    if most_predictive:
        top_word_indices = np.argsort(mult.todense().tolist()[0])[-3:][::-1]
        return [word_labels[idx] for idx in top_word_indices]
    
    else:
        bottom_word_indices = np.argsort(mult.todense().tolist()[0])[:3][::-1]
        return [word_labels[idx] for idx in bottom_word_indices]