# import pickle
import dill
import os
import random

# class GlobalVar:
#     clients = {random.randint(100,1000) : 'random test'}

class OnlineClientPool:
    __path = 'shared_data/clients.dill'

    def __init__(self):
        self.__data = {}
        self.__save() # clear the pickle file

    @staticmethod
    def get():
        if os.path.exists(OnlineClientPool.__path):
            return {}
        with open(OnlineClientPool.__path, 'rb') as rf:
            return dill.load(rf)

    def __save(self):
        with open(OnlineClientPool.__path, 'wb') as wf:
            dill.dump(self.__data, wf)

    def add(self, user_id, websocket):
        self.__data[user_id] = websocket
        self.__save()

    def remove(self, user_id):
        self.__data.pop(user_id)
        self.__save()
