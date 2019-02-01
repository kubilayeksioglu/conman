#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `conman` package."""


import unittest

from conman import Container
class  ROSMasterContainer(Container):
    image = 'awsurl/acrome/master:v1'
    container_name = 'rosmaster'
    ports = (3000, 8080, 9090)


class ROSSlaveContainer(Container):
    image = 'awsurl/acrome/slave:v1'
    container_name = 'rosslave'
    ports = (3000, 8080, 9090)

master_container = ROSMasterContainer(0)
master_container.start()

slave_container = ROSSlaveContainer(1)
slave_container = ROSSlaveContainer(2)
slave_container = ROSSlaveContainer(3)
slave_container = ROSSlaveContainer(4)


class TestConman(unittest.TestCase):
    """Tests for `conman` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

