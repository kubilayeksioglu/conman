======
conman
======

Docker Container Manager for Python

Install
-------

Install with::

    pip install git+https://github.com/kubilayeksioglu/conman.git

Usage
-----

Use as::

    from conman import TemplatedContainer

    class CustomContainer(ConmanContainer):
        image = "docker-image"
        ports = {'8080':'8080'}
        name = None
        name_template = "conman-%s"
        ports = None
        command = None
        volumes = {}
        network = None

    container = CustomContainer(1)
    container.start()  # starts 'conman-1' container
    container.get_host_address(8080) # returns "127.0.0.1:8080"

    container = CustomContainer(1)
    container.start(network='newnetwork')
    container.get_host_address(8080) # returns "$NETWORK_IP$:8080"

Check status of a container::

    container.status

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
