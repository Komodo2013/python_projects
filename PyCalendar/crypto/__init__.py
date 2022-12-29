import time

class AuthToken:

    def __init__(self, username, password):
        self.__create = time.time()

    def get_create(self):
        return self.__create

    create = property(get_create, None, None)


