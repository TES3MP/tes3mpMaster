import urllib2
import json
import time

_data = json.loads('{"port": 25565, "query_port": 25565, "motd": "A MOTD", "players": 0, "max_players": 20}')

print _data


def request(url, req_type, data=None):
    req = urllib2.Request(url)

    if req_type is not 'DELETE':
        req.data = data
        req.add_header('Content-Type', 'application/json')

    req.get_method = lambda: req_type
    f = urllib2.urlopen(req)
    response = f.read()
    print response
    f.close()


try:
    request("http://localhost:8080/api/servers", 'POST', json.dumps(_data))
    request("http://localhost:8080/api/servers/127.0.0.2:25565", 'DELETE')
except Exception as e:
    print e

update = True


while update:
    try:
        time.sleep(1)
        try:
            request("http://localhost:8080/api/servers/127.0.0.1:25565", 'PUT')
        except Exception as e:
            print e
    except KeyboardInterrupt:
        update = False
