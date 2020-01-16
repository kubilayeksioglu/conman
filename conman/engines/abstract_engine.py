class ConmanEngine:

    def run(self, name, image, **kwargs):
        raise NotImplementedError()

    def exec(self, container, command, output=False):
        raise NotImplementedError()

    def get(self, name):
        raise NotImplementedError()

    def stop(self, container):
        raise NotImplementedError()

    def inspect(self, container):
        raise NotImplementedError()

    def __del__(self):
        raise NotImplementedError()