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

    from conman import ConmanContainer

    class CustomContainer(ConmanContainer):
        image = "docker-image"
        container_name = "custom-name"
        local_ports = (8080)
        default_command = None

    from conman.utils import get_ip

    container = CustomContainer(1)
    container.start()
    container.get_host_address(8080) # returns "0.0.0.0:8081"

    container = CustomContainer(2)
    container.start(get_ip())
    container.get_host_address(8080) # returns "$WHATEVER_YOUR_IP_IS$:8082"

Check status of a container::

    container.status # returns either "exited" or "running"

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
