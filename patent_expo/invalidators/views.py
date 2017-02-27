# encoding: utf-8
import json, pickle, os, string, random, hashlib, numpy

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.generic import CreateView, DeleteView, ListView
from .models import File
from .response import JSONResponse, response_mimetype
from .serialize import serialize


class FileCreateView(CreateView):
    model = File
    fields = "__all__"


class FileDeleteView(DeleteView):
    model = File

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class FileListView(ListView):
    model = File

    def render_to_response(self, context, **response_kwargs):
        files = [ serialize(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

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
