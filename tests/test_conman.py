#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `conman` package."""
import os
import unittest

import docker

from conman import ConmanContainer
from conman.utils import get_ip

TESTS_DIR = os.path.dirname(__file__)


class GznodeContainer(ConmanContainer):
    image = "197358733965.dkr.ecr.eu-west-1.amazonaws.com/ride/ros-gazebo:v1.0"
    container_name = "test-gznode"
    local_ports = (8080,)
    default_command = None


class TestConman(unittest.TestCase):
    """Tests for `conman` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        # create dummy image with docker-py


    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_default_ip(self):
        """Test when no ip provided, does container receive correct host address (0.0.0.0)."""
        container = GznodeContainer(0)
        container.start()
        address = container.get_host_address(8080)
        expected = '0.0.0.0:8080'
        self.assertEqual(address, expected, "Default IP is incorrect. Expected: %s Actual: %s")
        container.stop()

    def test_autodetect_port(self):
        """
        Test if detecting port automatically works as expected
        :return:
        """
        container = GznodeContainer(1)
        container.start()
        address = container.get_host_address(8080)
        expected = '0.0.0.0:8081'
        self.assertEqual(address, expected, "Auto-detected port is wrong. Expected: %s Actual: %s")
        container.stop()

    def test_get_host_address(self):
        """
        Test if an IP is provided, can ConmanContainer bind that to IP address instead of 0.0.0.0
        :return:
        """
        local_ip = get_ip()

        container = GznodeContainer(1)
        container.start(local_ip)
        address = container.get_host_address(8080)
        expected = '%s:8081' % local_ip
        self.assertEqual(address, expected, "Host address is wrong. Expected: %s Actual: %s")
        container.stop()

    def test_volume(self):
        """
        Test if an IP is provided, can ConmanContainer bind that to IP address instead of 0.0.0.0
        :return:
        """
        source_path = os.path.abspath(TESTS_DIR)

        container = GznodeContainer(1)
        container.volumes = {source_path: {
            'bind': '/colab',
            'mode': 'rw'
        }}
        container.start()

        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        inspection = client.inspect_container(container.container.id)

        container.stop()
        client.close()

        expected = source_path
        actual = inspection['Mounts'][0]['Source']
        self.assertEqual(actual, expected, "Host address is wrong. Expected: %s Actual: %s" % (actual, expected))


if __name__ == "__main__":
    unittest.main()

