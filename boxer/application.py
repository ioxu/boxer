class Application(object):
    """"root application object"""

    application_meta = {}

    def __init__(self,
            name = "default application name"):
        self.name = name
        print("starting %s"%self)


    def message(self, message):
        """display a message"""
        print("Application(%s).message: %s"%message)

