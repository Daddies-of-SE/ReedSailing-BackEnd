import pickle
import os
import random

class GlobalVar:
    clients = {random.randint(100,1000) : 'random test'}

class Client:
    def __init__(self):
        self.__data = {}
        self.__path = 'shared_data/client.pickle'
        self.__save() # clear the pickle file

    def get(self):
        if os.path.exists(self.__path):
            self.__data = {}
            return {}
        with open(self.__path, 'rb') as rf:
            self.__data = pickle.load(rf)
        return self.__data

    def __save(self):
        with open(self.__path, 'wb') as wf:
            pickle.dump(self.__data, wf)

    def add(self, user_id, websocket):
        self.__data[user_id] = websocket
        self.__save()
