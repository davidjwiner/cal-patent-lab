# encoding: utf-8
import json, pickle, os, string, random, hashlib, numpy

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.generic import CreateView, DeleteView, ListView
from django.core.files.storage import FileSystemStorage

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

import sys
sys.path.append(sys.path[0]+'/ml-algorithms')
import case_prediction


# This function renders the main page
def index(request):
    """
    View function for home page of site.
    """
    
    # Render the HTML template index.html
    return render(
        request,
        'index.html'
    )

def predict(request, *args, **kwargs):
    if request.method == 'POST':
    	patent = ""
    	# try getting patent text from file
    	patent += request.POST.get('textfield', None)
        # get outcome type
        outcome = request.POST.get('outcome', None)

        #calculate probability 
        probability = case_prediction.predict_probability(patent,outcome)
        color = ""
        if probability < .25:
            color = "green"
        elif probability < .75:
            color = "yellow"
        else:
        	color = "red"
        response = "There is a <span style='color:"+color+"'>{0:.1f}%</span>".format(probability*100)
        response += " chance of "+outcome+". <br/>"

        # get words
        words = case_prediction.get_top_keywords(patent,outcome)
        response += "The words generating the most conflict are:<br/> <ul> "
        for word in words:
        	response += "<li>"+word+"</li>"
        response += "</ul>"

        return HttpResponse(json.dumps({'response': response}), content_type="application/json")

# Call this with an AJAX request. If the user uploads a text file, populate the text field
def getText(request , *args, **kwargs):
	file = request.FILES["patentFile"]
	response = file.read()
	return HttpResponse(json.dumps({'response': response}), content_type="application/json")

def search(request, patentId):
	return

def stats(request):
	return render(
        request,
        'stats.html'
    )
