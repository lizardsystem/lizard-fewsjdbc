Code documentation
==================

(Note: the REST api is documented separately).


Database model
--------------

There's just one database model for storing the jdbc connection data.
But it *does* contain all the business logic for accessing the FEWS
data.

.. automodule:: lizard_fewsjdbc.models
   :members:


Browser interaction (views)
---------------------------

.. automodule:: lizard_fewsjdbc.views
   :members:


Lizard map adapter
------------------

.. automodule:: lizard_fewsjdbc.layers
   :members:
