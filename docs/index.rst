Welcome to cfglib's documentation!
=============================================================================

Contents
--------

.. toctree::
   :maxdepth: 1

   installation
   usage
   cfglib
   history


Example
-------
.. code-block:: python

    class PointConfig(cfglib.SpecValidatedConfig):
        x = cfglib.IntSetting()
        y = cfglib.IntSetting()


    class ExampleToolConfig(cfglib.SpecValidatedConfig):
        message = cfglib.StringSetting(default='Hello!')
        config_file = cfglib.StringSetting(default=None)
        points = cfglib.ListSetting(
            subsetting=cfglib.DictSetting(subtype=PointConfig),
        )

    cfg = ExampleToolConfig([
        {'points': [{'x': 1, 'y': 2}]},
        EnvConfig(prefix='EXAMPLE_', lowercase=True),
    ])

    print(cfg.message)
    # when run with EXAMPLE_MESSAGE=hello will print hello

    print(cfg.points)
    # will print [<PointConfig {'x': 1, 'y': 2}>]



Description
-----------

.. include:: ../README.rst


Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
