# -*- coding: utf-8 -*-

"""Top-level package for conman."""

__author__ = """Kubilay Eksioglu"""
__email__ = 'kubilayeksioglu@gmail.com'
__version__ = '0.1.3'


from conman.conman import ConmanContainer

class SlaveContainer(ConmanContainer):

    image = 'ride-gznode'
    container_name = 'arena-slave'
    local_ports = (8080,)
