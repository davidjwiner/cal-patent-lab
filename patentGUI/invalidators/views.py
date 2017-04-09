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
        
        probability = case_prediction.predict_probability(patent)

        color = ""
        if probability < .25:
            color = "green"
        elif probability < .75:
            color = "yellow"
        context = {
            'probability': "{0:.1f}".format(probability*100),
            'color': color
        }
        response = "There is a {0:.1f}".format(probability*100)+"% chance of invalidation."
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
# Create your views here.
