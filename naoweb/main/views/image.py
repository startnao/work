import base64
from PIL import Image
from django.http import HttpResponse
from main.naotcp import *

def image_action(request):
    connection = nao_connect()
    data = nao_action(connection, "camera")

    print(data[0:500])

    data = base64.b64decode(data)
    nao_disconnect(connection)

    img = Image.frombytes("RGB", (320, 240), data)
    response = HttpResponse(content_type='image/jpeg')
    img.save(response, "JPEG")

    return response
