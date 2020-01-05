#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `conman` package."""
import os
import unittest

from conman import DockerEngine, ConmanContainer
from tests.constants import ALPINE_IMAGE

TESTS_DIR = os.path.dirname(__file__)
CONMAN_TEST_NETWORK = "conman-test-network"
CONMAN_TEST_CONTAINER = "conman-test-container"


class TestDockerEngine(unittest.TestCase):
    """Tests for `conman` package."""

    container = None

    def setUp(self) -> None:
        self.container = ConmanContainer(DockerEngine, CONMAN_TEST_CONTAINER)
        if self.container.is_running:
            self.container.stop()

    def tearDown(self) -> None:
        self.container.stop()

    def test_port(self):
        """
        Test if Docker Container connects to the correct port
        """
        self.container.start(ALPINE_IMAGE, ports={"8888": "8888"})
        inspection = self.container.inspect()

        expected = [{"HostIp": "0.0.0.0", "HostPort": "8888"}]
        port_info = inspection['NetworkSettings']['Ports'].get('8888/tcp')
        self.assertEqual(port_info, expected, "Port is different than what is expected")

    def test_get_host_address(self):
        """
        Test if can ConmanContainer returns correct address info
        """
        self.container.start(ALPINE_IMAGE, ports={"8888": "8888"})

        expected = ("127.0.0.1", "8888")
        self.assertEqual(self.container.get_host_address(8888), expected, "Address is different than what is expected")

    def test_network_alias(self):
        aliases = ['c1']
        self.container.start(ALPINE_IMAGE, network=CONMAN_TEST_NETWORK, network_aliases=aliases)

        attrs = self.container.inspect()
        container_network_aliases = attrs['NetworkSettings']['Networks'][CONMAN_TEST_NETWORK]['Aliases']
        self.assertTrue(all([a in container_network_aliases for a in aliases]))
