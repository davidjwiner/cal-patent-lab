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
sys.path.append(sys.path[0]+'/patentGUI/mlalgorithms')
import case_denial


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
    	try:
    		patent= request.FILES['patentFile'].read()
    	except: # if not, get it from text field
    		patent = request.POST.get('textfield', None)
        	patent = str(patent)
        
        patent = "".join(l for l in patent if l not in string.punctuation)
        patent = "".join(patent.split())
        patent = patent.lower()
        hashed_number = int(hashlib.md5(patent).hexdigest()[:8],16)
        print(hashed_number)
        numpy.random.seed(hashed_number)
        probability = case_denial.denial_probability(patent)
        
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
def getText(request):

	return

def result(request, template = "invalidators/result.html"):
    if request.method == 'POST':    
        return HttpResponseRedirect('/upload/home/')
    return render(request, template);

def search(request, patentId):
	return

def stats(request):
	return
# Create your views here.
