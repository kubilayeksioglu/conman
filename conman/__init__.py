# -*- coding: utf-8 -*-

"""Top-level package for conman."""

__author__ = """Kubilay Eksioglu"""
__email__ = 'kubilayeksioglu@gmail.com'
__version__ = '0.2.0'


import logging
import docker
from docker.errors import NotFound as DockerNotFound
logger = logging.getLogger(__name__)


class ContainerNotRunning(Exception):
    pass


class DockerEngine:

    def __init__(self):
        self._client = docker.from_env()

    def run(self, name, image, ports=None, expose=None, command=None, volumes={}, network=None):
        if network is not None:
            try:
                _ = self._client.networks.get(network)
            except DockerNotFound:
                self._client.networks.create(network, driver="bridge")


        self._client.containers.run(image, 
                                    stdin_open=True, 
                                    tty=True, 
                                    command="/bin/sh", 
                                    ports=ports, 
                                    name=name, 
                                    detach=True,
                                    network=network, 
                                    volumes=volumes)

        # send a default command, in case
        if command:
            container = self.get(name)
            self.exec(container, command)

    def exec(self, container, command, output=False):
        """
        Send a bash command to the container

        :param command: str     Command to be run
        :param output: bool     Whether Conman should wait for the output or detach immediately.
        :return: None if output=False, (exit code: int, msg: str) pairs otherwise
        """
        if not output:
            container.exec_run("sh -c '%s'" % command, detach=True)
            return None

        exit_code, stream_msgs = container.exec_run("sh -c '%s'" % command, stream=True)
        return exit_code, [msg.decode('utf-8') for msg in stream_msgs]

    def get(self, name):
        try:
            container = self._client.containers.get(name)
        except DockerNotFound:
            return None

        # if container is exited, we simply remove it
        if container.status == 'exited':
            container.remove()
            return None
        
        return container

    def stop(self, container):
        container.stop()
        container.remove()

    def inspect(self, container):
        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        inspection = client.inspect_container(container.id)
        client.close()

        return inspection

    def __del__(self):
        self._client.close()


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

    def start(self, image, **kwargs):
        container = self.engine.get(self.name)
        if container:
            logger.warning("Container %s is already running" % self.name)
            return

        self.engine.run(self.name, image, **kwargs)

    def status(self):
        return self.engine.status(self.container)

    def stop(self):
        self.engine.stop(self.container)

    def exec(self, command, output=True):
        return self.engine.exec(self.container, command, output=output)

    def inspect(self):
        return self.engine.inspect(self.container)


RUN_CONFIG_KEYS = ['ports', 'command', 'expose', 'volumes', 'network']


class TemplatedContainer(ConmanContainer):

    image = None
    name = None
    name_template = None
    ports = None
    command = None
    expose = None
    volumes = {}
    network = None

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
        runconfig = {k:getattr(self, k) for k in RUN_CONFIG_KEYS}
        image = image if image else self.image
        super().start(image, **runconfig)
