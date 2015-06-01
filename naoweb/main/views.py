import json

from django.http import HttpResponse
from django.shortcuts import render_to_response

def index_action(request):
    return render_to_response('index.html')

def execute_action(request, name):
    return HttpResponse(json.dumps({"message": name}), content_type="application/json")
