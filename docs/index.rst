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
* django-channels (in combination with `relay subscriptions <https://facebook.github.io/relay/docs/en/subscriptions.html>`_ )
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

Things to explore
-----------------

* logging and progress information for insight into what the app is doing (e.g structured logs with eliot combined with a convention on how to log progress and an easy way to show progress to the end user too)
* push updates to ui with websockets
* collect stats from the connected camera devices (https://github.com/timescale/timescaledb)


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    index
    diagram-tests
