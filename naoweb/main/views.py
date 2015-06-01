import json
import base64
from PIL import Image

from django.http import HttpResponse
from django.shortcuts import render_to_response

def index_action(request):
    return render_to_response('index.html')

def execute_action(request, name):
    return HttpResponse(json.dumps({"message": name}), content_type="application/json")

def image_action(request):
    data = open('/home/tgalopin/Projets/Python/startnao/naoweb/main/image.base64', 'rb').read()
    data = base64.b64decode(data)

    img = Image.fromstring("RGB", (320, 240), data)
    img.save('/home/tgalopin/Projets/Python/startnao/naoweb/main/image.jpg')

    response = HttpResponse(content_type='image/jpeg')
    img.save(response, "JPEG")

    return response
