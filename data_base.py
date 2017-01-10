import json
from threading import Lock

def is_string(_str):
    return type(_str) is str or type(_str) is unicode

class DataBase:
    __db = {}
    __db_mutex = {}

    def __check_types(self, ip, port, query_port, hostname, modname, players, max_players, last_update):
        if is_string(ip) \
                and type(port) is int and type(query_port) is int and is_string(hostname) \
                and type(players) is int and type(max_players) is int and type(last_update) is int\
                and is_string(modname):
            return True
        return False
    
    def __id(self, addr, port):
        return addr + ':' + str(port)

    def if_exists(self, id):
        return id in self.__db

    def __update(self, ip, port, query_port, hostname, modname, players, max_players, last_update):
        id = self.__id(ip, port)
        with self.__db_mutex[id]:
            self.__db[id]['query_port'] = query_port
            self.__db[id]['hostname'] = hostname
            self.__db[id]['modname'] = modname
            self.__db[id]['players'] = players
            self.__db[id]['max_players'] = max_players
            self.__db[id]['last_update'] = last_update

    def add(self, ip, port, query_port, hostname, modname, players, max_players, last_update):
        if not self.__check_types(ip, port, query_port, hostname, modname, players, max_players, last_update):
            return

        id = self.__id(ip, port)

        if self.if_exists(id):
            return

        self.__db[id] = {}
        self.__db_mutex[id] = Lock()

        self.__update(ip, port, query_port, hostname, modname, players, max_players, last_update)
        return id

    # todo: need partial update support
    def update(self, ip, port, query_port, hostname, modname, players, max_players, last_update):
        id = self.__id(ip, port)
        if not self.if_exists(id):
            return
        if not self.__check_types(ip, port, query_port, hostname, modname, players, max_players, last_update):
            return
        self.__update(ip, port, query_port, hostname, modname, players, max_players, last_update)

    def resetTimer(self, id):
        with self.__db_mutex[id]:
            self.__db[id]['last_update'] = 0

    @property
    def db(self):
        return self.__db

    def delete(self, id):
        with self.__db_mutex[id]:
            if id not in self.__db:
                return
            self.__db.pop(id)
            self.__db_mutex.pop(id)

    def update_time(self, id, sec):
        with self.__db_mutex[id]:
            self.__db[id]['last_update'] += sec
