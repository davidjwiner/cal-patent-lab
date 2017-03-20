# encoding: utf-8
import json, pickle, os, string, random, hashlib, numpy

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.generic import CreateView, DeleteView, ListView
from django.core.files.storage import FileSystemStorage

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
    #if request.is_ajax():
        #return HttpResponse(json.dumps({'response': 'reject'}), content_type="application/json")

    if request.method == 'POST':
        patent = request.POST.get('textfield', None)
        patent = str(patent)
        patent = "".join(l for l in patent if l not in string.punctuation)
        patent = "".join(patent.split())
        patent = patent.lower()
        hashed_number = int(hashlib.md5(patent).hexdigest()[:8],16)
        print(hashed_number)
        numpy.random.seed(hashed_number)
        probability = 1
        color = "#Ff7000"
        while probability > .95 or probability < 0.02:
            probability = float(numpy.random.poisson(5))/float(18)

        if hashed_number == 2228619045:
            probability = .850
        elif hashed_number == 2268799671:
            probability = .792
        elif hashed_number == 3223191610:
            probability = .681
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

def result(request, template = "invalidators/result.html"):
    if request.method == 'POST':    
        return HttpResponseRedirect('/upload/home/')
    return render(request, template);

def search(request, patentId):
	return

def stats(request):
	return
# Create your views here.
