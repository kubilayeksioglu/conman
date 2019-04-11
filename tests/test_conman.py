#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `conman` package."""
import os
import unittest

from conman import TemplatedContainer, DockerEngine, ContainerNotRunning

TESTS_DIR = os.path.dirname(__file__)


CONMAN_TEST_PYTHON_NETWORK = "conman-test-python-network"


class PythonContainer(TemplatedContainer):
    image = "python:3.7-slim"
    ports = {'8080':'8080'}
    command = "python3 -m http.server 8080"
    name = "conman-test-python"

class NetworkPythonContainer(TemplatedContainer):
    image = "python:3.7-slim"
    ports = {'8081':'8081'}
    network = "conmantest"
    command = "python3 -m http.server 8081"
    name = CONMAN_TEST_PYTHON_NETWORK

class WgetContainer(TemplatedContainer):
    image = "inutano/wget:latest"
    network = "conmantest"
    name = "conman-test-wget-network"

class TestConman(unittest.TestCase):
    """Tests for `conman` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        # create dummy image with docker-py

    def _stop(self, container):
        try:
            container.stop()
        except ContainerNotRunning:
            pass


    def tearDown(self):
        """Tear down test fixtures, if any."""
        self._stop(PythonContainer(DockerEngine))
        self._stop(NetworkPythonContainer(DockerEngine))
        self._stop(WgetContainer(DockerEngine))

    def test_port(self):
        """Test when no ip provided, does container receive correct host address (0.0.0.0)."""
        container = PythonContainer(DockerEngine)
        container.start()
        inspection = container.inspect()

        expected = [{"HostIp": "0.0.0.0", "HostPort": "8080"}]
        port_info = inspection['NetworkSettings']['Ports'].get('8080/tcp')
        self.assertEqual(port_info, expected, "Port is different than what is expected")

        # expected = '0.0.0.0:8080'
        # self.assertEqual(address, expected, "Default IP is incorrect. Expected: %s Actual: %s")
        container.stop()

    def test_network(self):
        """Test when no ip provided, does container receive correct host address (0.0.0.0)."""
        python_container = NetworkPythonContainer(DockerEngine, name=CONMAN_TEST_PYTHON_NETWORK)
        python_container.start()

        wget_container = WgetContainer(DockerEngine)
        wget_container.start()

        error_code, lines = wget_container.exec('wget -q -O - \"$@\" http://%s:8081' % CONMAN_TEST_PYTHON_NETWORK, output=True)
        self.assertTrue(lines[0].startswith('<!DOCTYPE HTML PUBLIC'))

        # expected = '0.0.0.0:8080'
        # self.assertEqual(address, expected, "Default IP is incorrect. Expected: %s Actual: %s")
        python_container.stop()
        wget_container.stop()


    # def test_autodetect_port(self):
    #     """
    #     Test if detecting port automatically works as expected
    #     :return:
    #     """
    #     container = GznodeContainer(1)
    #     container.start()
    #     address = container.get_host_address(8080)
    #     expected = '0.0.0.0:8081'
    #     self.assertEqual(address, expected, "Auto-detected port is wrong. Expected: %s Actual: %s")
    #     container.stop()

    # def test_get_host_address(self):
    #     """
    #     Test if an IP is provided, can ConmanContainer bind that to IP address instead of 0.0.0.0
    #     :return:
    #     """
    #     local_ip = get_ip()

    #     container = GznodeContainer(1)
    #     container.start(local_ip)
    #     address = container.get_host_address(8080)
    #     expected = '%s:8081' % local_ip
    #     self.assertEqual(address, expected, "Host address is wrong. Expected: %s Actual: %s")
    #     container.stop()

    # def test_volume(self):
    #     """
    #     Test if an IP is provided, can ConmanContainer bind that to IP address instead of 0.0.0.0
    #     :return:
    #     """
    #     source_path = os.path.abspath(TESTS_DIR)

    #     container = GznodeContainer(1)
    #     container.volumes = {source_path: {
    #         'bind': '/colab',
    #         'mode': 'rw'
    #     }}
    #     container.start()

    #     client = docker.APIClient(base_url='unix://var/run/docker.sock')
    #     inspection = client.inspect_container(container.container.id)

    #     container.stop()
    #     client.close()

    #     expected = source_path
    #     actual = inspection['Mounts'][0]['Source']
    #     self.assertEqual(actual, expected, "Host address is wrong. Expected: %s Actual: %s" % (actual, expected))


if __name__ == "__main__":
    unittest.main()

