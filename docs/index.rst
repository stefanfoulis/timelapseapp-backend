TimelapseApp's documentation!
=============================

TimelapseApp will be a web application built to create timelapse videos. It is
connected to cameras which can send images.


.. warning:: Nearly none of this actually exists yet. This are just my list of
             wild ideas.


backend
-------

* django with a graphql API
* django-celery for background tasks
* django-channels
* moviepy to generate movies

ui
--

* node server
* react & relay (talks to graphql api of backend)
* google material design

cameras
-------

* RaspberryPi (Zero?) with camera module
    * alternative: RaspberryPi that talks to a GoPro
* Can run in online and offline mode
* delivers images to backend over wifi/4G/LAN



.. toctree::
    :maxdepth: 2
    :caption: Contents:

    diagram-tests
