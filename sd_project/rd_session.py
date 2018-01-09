import redis
import uuid


class Manager:
    def __init__(self, connection=None):
        self.connection = connection or redis.StrictRedis(
            host="192.168.1.220",
            port=8888
        )
        self.name = "sd_project"

    def set(self, key, value):
        return self.connection.set(key, value)

    def get(self, key):
        return self.connection.get(key)

    @staticmethod
    def uuid():
        return uuid.uuid1()

    def create_session(self, _id):
        _uuid = self.uuid()

        self.set("{}:{}".format(self.name, _id), _uuid)
        self.set("{}".format(_uuid), _id)

        return _uuid

sessions = Manager()
#
# # test.create_session(_id="helloworld!")
#
# print(test.get("26be104b-1544-3a1d-bbda-76d5b32be521"))
