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

    class ExampleToolConfig(cfglib.SpecValidatedConfig):
        message = cfglib.StringSetting(default='Hello!')
        config_file = cfglib.StringSetting(default=None)


    cfg = ExampleToolConfig([
        EnvConfig(prefix='EXAMPLE_', lowercase=True),
    ])

    print(cfg.message)
    # when run with EXAMPLE_MESSAGE=hello will print hello



Description
-----------

.. include:: ../README.rst


Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
