import json
from main.naotcp import *
from django.http import HttpResponse

def execute_action(request, name):
    connection = nao_connect()
    nao_action(connection, name)
    nao_disconnect(connection)

    return HttpResponse(json.dumps({'action': name, 'status': 'ok'}), content_type='application/json')
