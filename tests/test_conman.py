#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `conman` package."""


import unittest
from conman import ConmanContainer
from conman.utils import get_ip


class GznodeContainer(ConmanContainer):
    image = "ride-gznode"
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

