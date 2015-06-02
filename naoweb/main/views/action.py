import json
from main.naotcp import *
from django.http import HttpResponse

def execute_action(request, name):
    parts = name.split('-')

    command = parts[0]
    parameters = ''

    if len(parts) == 2:
        parameters = '#' + parts[1].replace('_', ' ')

    connection = nao_connect()
    nao_action_udp(connection, command + parameters)
    nao_disconnect(connection)

    return HttpResponse(json.dumps({'action': name, 'status': 'ok'}), content_type='application/json')
