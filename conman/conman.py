# -*- coding: utf-8 -*-

"""Main module."""
import docker
from docker.errors import NotFound as DockerNotFound
import logging

from conman.errors import ContainerPortAutoAssignError, ContainerNotRunning

logger = logging.getLogger(__name__)

STATUS_NOT_RUNNING, STATUS_RUNNING = 'exited', 'running'


def clean_ports(dct):
    return {str(k):str(v) for k, v in dct.items()}


class AbstractConmanContiner:

    def __init__(self, _id):
        self._id = _id

    @property
    def status(self):
        raise NotImplementedError()

    def start(self, port=8080):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def start_server(self):
        raise NotImplementedError()


class ConmanContainer:

    image = None
    container_name = None
    local_ports = None

    def __init__(self, _id):
        """
        Dockerized simulator class

        :param: _id   ID of the container. As long as it is unique, it can be a string or int
        """
        self.id = _id
        self.name = "%s-%s" % (self.__class__.container_name, _id)
        self.client = docker.from_env()

        # holds private container
        self._container = None

    @property
    def ports(self):
        """
        Port configuration for the container. Returns the same result as `.attrs['NetworkSettings']['Ports']`
        for a Docker Container
        :return: Dict
        """
        # if container is not running, it's ports are not available
        if not self.container:
            raise ContainerNotRunning()

        # container is running, but self._ports is not set, this means, Cona
        return self.container.attrs['NetworkSettings']['Ports']

    def get_host_address(self, port, protocol='tcp'):
        """
        Returns the host address for a local port
        :param port: Port that is exposed by container
        :param protocol: Protocol used for exposing the port of container
        :return: str
        """
        conf = self.ports["%s/%s" % (port, protocol)][0]
        return "%(HostIp)s:%(HostPort)s" % conf

    @property
    def container(self):
        """
        Returns the underlying Docker Container for this ConmanContainer object.
        :return:
        """
        if self._container:
            return self._container
        else:
            self._container = self._get_container()

        return self._container

    def _get_container_or_error(self):
        try:
            return self.client.containers.get(self.name)
        except DockerNotFound as e:
            logger.exception("Docker with id %s not found." % self.name)
            raise ContainerNotRunning()

    def _get_container(self):
        try:
            container = self.client.containers.get(self.name)
            # if container is exited, we simply remove it & return None
            if container.status == 'exited':
                container.remove()
                return None
            return container
        except DockerNotFound as e:
            return None

    @property
    def status(self):
        """
        Return the status of the underlying container

        :return: str
        """
        if not self.container:
            return STATUS_NOT_RUNNING

        return self.container.status

    def _image_exists(self):
        """
        Check if image is downloaded & in the local system

        :return: bool
        """
        try:
            self.client.images.get(self.__class__.image)
            return True
        except docker.errors.ImageNotFound:
            return False

    def __generate_ports(self):
        """
        Generate ports according to id of the container

        :return: Dict
        """
        # we cannot deduce if id is not int
        if type(self.id) != int:
            raise ContainerPortAutoAssignError()

        # if container ports is None, we dont have to generate ports
        container_ports = self.__class__.local_ports
        if container_ports is None:
            return None

        # we simply add id of the container to the ports
        return clean_ports({p: (p + self.id) for p in container_ports})

    def start(self, ports=None):
        """
        Starts a container
        If a container with object id already exists, raises DockerServerExistsError.
        If no such server found, runs requested server in Docker Engine.

        :raises: DockerExists
        :return: None
        """
        if self.container:
            logger.warning("Container already is running, will not try to restart")
            return

        # TODO: provide a mechanism for reporting progress
        if not self._image_exists():
            logger.warning("Image %s not found in local filesystem. "
                           "Downloading the image, this may take a while." % self.image)

        # use user provided ports or generate your own port mapping
        if not ports:
            ports = self.__generate_ports()

        # run container
        self.client.containers.run(self.image,
                                   name=self.name,
                                   ports=clean_ports(ports),
                                   detach=True,  # daemon mode
                                   stdin_open=True, tty=True, command="/bin/bash"
                                   )

    def stop(self):
        """
        Stop a container if exists

        :return: None
        """
        if self.container is None:
            raise ContainerNotRunning()

        self.container.stop()
        self.container.remove()

        # TODO: Move this to a more fitting call
        self.client.containers.prune()  # remove stopped dockers
