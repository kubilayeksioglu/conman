# -*- coding: utf-8 -*-

"""Top-level package for conman."""

__author__ = """Kubilay Eksioglu"""
__email__ = 'kubilayeksioglu@gmail.com'
__version__ = '0.2.11'

import logging
from sys import platform

logger = logging.getLogger(__name__)


class ContainerNotRunning(Exception):
    pass


class ConmanContainer:

    def __init__(self, engine, name, engine_params={}):
        self.engine = engine(**engine_params)
        self.name = name

    @property
    def container(self):
        container = self.engine.get(self.name)
        if container:
            return container
        else:
            raise ContainerNotRunning()

    @property
    def is_running(self):
        try:
            _ = self.container
            return True
        except ContainerNotRunning:
            return False

    def start(self, image, **kwargs):
        container = self.engine.get(self.name)
        if container:
            logger.warning("Container %s is already running" % self.name)
            return

        self.engine.run(self.name, image, **kwargs)

    def stop(self):
        self.engine.stop(self.container)

    def exec(self, command, output=True):
        return self.engine.exec(self.container, command, output=output)

    def inspect(self):
        return self.engine.inspect(self.container)


RUN_CONFIG_KEYS = ['ports', 'command', 'volumes', 'network', 'auth']


class TemplatedContainer(ConmanContainer):
    image = None
    name = None
    name_template = None
    ports = None
    command = None
    volumes = {}
    network = None
    auth = None

    def __init__(self, engine, id=None, name=None, engine_params={}, **kwargs):
        if name is None:
            if id:
                name = self.name_template % id
            else:
                name = self.name
        if name is None:
            raise RuntimeError("cls.name, id or name should be provided")
        super().__init__(engine, name, engine_params)

        for key in ['image'] + RUN_CONFIG_KEYS:
            setattr(self, key, kwargs.get(key, getattr(self.__class__, key)))

    def start(self, image=None, **kwargs):
        runconfig = {k: getattr(self, k) for k in RUN_CONFIG_KEYS}

        runconfig.update(kwargs)

        image = image if image else self.image
        super().start(image, **runconfig)
