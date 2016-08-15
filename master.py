#!/usr/bin/env python
import web
import json
import time
import threading

from restful_controller import RESTfulController
from data_base import DataBase

db = DataBase()
stop_timer = False
buffered_db = {}
buffered_db_lock = threading.Lock()

ValidIpAddressRegex = "(?:[0-9]{1,3}\.){3}[0-9]{1,3}"
ValidHostnameRegex = "(?:[a-z0-9]+(?:-[a-z0-9]+)*\.+[a-z]{2,})"
ValidPortRegex = "(?:[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"

urls = (
    # r'/api/servers(?:/(?P<server_id>' + ValidHostnameRegex + '))?', 'MasterServerController',
    r'/api/servers(?:/(?P<server_id>' + ValidIpAddressRegex + '\:' + ValidPortRegex + '))?', 'MasterServerController',
)

app = web.application(urls, locals())


def updater():
    while not stop_timer:
        for server_id in db.db.keys():
            db.update_time(server_id, 1)
            if db.db[server_id]['last_update'] >= 60:
                db.delete(server_id)

        with buffered_db_lock:
            app.fvars['buffered_db'] = json.dumps(db.db)  # hack
        time.sleep(1)


class MasterServerController(RESTfulController):
    def list(self):
        with buffered_db_lock:
            return {"list servers": buffered_db}

    def get(self, server_id):
        if db.if_exists(server_id):
            return "server", db.db[server_id]
        else:
            raise web.badrequest

    def create(self):
        response = False
        resource = json.loads(web.data())

        try:
            db.add(ip=web.ctx['ip'], last_update=0, **resource)
            response = True
        except Exception as e:
            # todo: necessary to ban after the CONFIG.MAX_ATTEMPTS for the CONFIG.BAN_TIMER
            print (str(web.ctx['ip']) + ': Error in request on create list (' + str(e) + ').')
            raise web.badrequest

        raise web.created

    def update(self, server_id):
        print server_id
        response = False
        if str(server_id).find(web.ctx['ip']) != -1 and db.if_exists(server_id):
            if not web.data():  # empty request
                db.resetTimer(server_id)
                response = True
            else:
                try:
                    resource = json.loads(web.data())
                    db.update(ip=web.ctx['ip'], last_update=0, **resource)
                    response = True
                except Exception as e:
                    # todo: necessary to ban after the CONFIG.MAX_ATTEMPTS for the CONFIG.BAN_TIMER
                    print (str(web.ctx['ip']) + ': Error in request on update list (' + str(e) + ').')
                    raise web.badrequest
                    web.ctx
        else:
            print (str(web.ctx['ip']) + ': Trying to update a non-existent server or without permissions.')
            raise web.badrequest

        raise web.accepted

    def delete(self, server_id):
        response = False
        # if str(server_id).find(web.ctx['ip']) == -1:
        #    print (str(web.ctx['ip']) + ': Trying to delete without permissions.')
        # else:
        #    db.delete(server_id)
        #    response = True
        raise web.accepted


if __name__ == "__main__":
    thr = threading.Thread(target=updater)
    thr.start()
    app.run()

    stop_timer = True
    thr.join()
    print 'Server is stopped!'
