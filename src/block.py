class Block(object):
    def __init__(self, name, initial_state):
        self.__name = name
        self.__initial_state = initial_state
        self.__commands = {}

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def initial_state(self):
        return self.__initial_state

    @initial_state.setter
    def initial_state(self, initial_state):
        self.__initial_state = initial_state

    @property
    def commands(self):
        return self.__commands

    @commands.setter
    def commands(self, commands):
        self.__commands = commands

    def __str__(self):
        return "Name: "+self.__name+" state: "+int(self.__initial_state)
