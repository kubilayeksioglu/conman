import docker
import logging
from docker.errors import NotFound as DockerNotFound
from .abstract_engine import ConmanEngine


logger = logging.getLogger(__name__)


def f():
    pass


class DockerEngine(ConmanEngine):

    def __init__(self):
        self._client = docker.from_env()

    def run(self, name, image, network=None, auth=None, network_aliases=[], **kwargs):
        # get or create network, if provided
        docker_network = None
        if network is not None:
            try:
                docker_network = self._client.networks.get(network)
            except DockerNotFound:
                logger.info("Creating network: %s" % network)
                docker_network = self._client.networks.create(network, driver="bridge")

        # if auth is provided, login
        if auth:
            # enable no param functions
            if type(auth) == type(f):
                auth = auth()
            self._client.login(**auth)

        # here we check if the image exists, pull otherwise
        try:
            self._client.images.get(image)
        except docker.errors.ImageNotFound:
            logger.warning("Pulling %s. This may take a while" % image)
            self._client.images.pull(image)

        logger.info("Starting image: %s" % image)
        container = self._client.containers.create(image, stdin_open=True, tty=True, detach=True, name=name, **kwargs)

        # start the container
        container.start()

        if docker_network:
            docker_network.connect(container, aliases=network_aliases)

        logger.info("Image start completed: %s" % image)

    def exec(self, container, command, output=False):
        """
        Send a bash command to the container

        :param container: Container     Docker Container to run the command on.
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


