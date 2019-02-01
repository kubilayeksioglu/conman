# -*- coding: utf-8 -*-

"""Main module."""
import docker
from docker.errors import NotFound as DockerNotFound
import logging

from conman.errors import ContainerDoesNotExist, ContainerExists, ContainerPortAutoAssignError

logger = logging.getLogger(__name__)

STATUS_NOT_RUNNING, STATUS_RUNNING = 'exited', 'running'


def clean_ports(dct):
    return {str(k):str(v) for k, v in dct.items()}


class AbstractContiner:

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


class Container:

    image = None
    container_name = None
    ports = None

    def __init__(self, _id):
        """
        Dockerized simulator class

        :param: _id   ID of the container. As long as it is unique, it can be a string or int
        """
        self.id = _id
        self.name = "%s-%s" % (self.__class__.container_name, _id)
        self.client = docker.from_env()

    def _get_container_or_error(self):
        try:
            return self.client.containers.get(self.name)
        except DockerNotFound as e:
            logger.exception("Docker with id %s not found." % self.name)
            raise ContainerDoesNotExist()

    def _get_container(self):
        try:
            return self.client.containers.get(self.name)
        except DockerNotFound as e:
            return None

    @property
    def status(self):
        """
        Return the status of the underlying container

        :return: str
        """
        container = self._get_container()
        if not container:
            return STATUS_NOT_RUNNING

        return container.status

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
        container_ports = self.__class__.ports
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
        # check if already a server with the same id exists,
        # if not create one
        try:
            container = self.client.containers.get(self.name)

            # if container exited but still in the list, remove
            if container.status == 'exited':
                container.remove()
            else:
                raise ContainerExists()
        except DockerNotFound as e:
            pass

        # TODO: provide a mechanism for reporting progress
        if not self._image_exists():
            logger.warning("Image %s not found in local filesystem. Downloading the image, this may take a while." % IMAGE)

        # use user provided ports or generate your own port mapping
        port_mapping = clean_ports(ports) if ports else self.__generate_ports()

        # run container
        self.client.containers.run(self.image,
                                   name=self.name,
                                   ports=port_mapping,
                                   detach=True,  # daemon mode
                                   stdin_open=True, tty=True, command="/bin/bash"
                                   )

    def stop(self):
        """
        Stop a container if exists

        :return: None
        """
        container = self._get_container_or_error()
        container.stop()
        container.remove()

        # TODO: Move this to a more fitting call
        self.client.containers.prune()  # remove stopped dockers
