EXPERIMENTAL WORK-IN-PROGRESS REST API THINKWORK!!!!
====================================================

Some of Reinout's thoughts on a proper REST api:

- **Linked data**.  No magic URLs which you have to know exactly.  From a root
  URL, you should be able to find everything you need by just following the
  URLs.  So not a list of IDs of something that you have to hand-craft a URL
  with, but simply a list of URLs with the ID already included.

- **Json**.  In principle, json is returned.  No html, no xml.  Json is the
  de-facto simple data exchange format nowadays.  Images, html, wms: those are
  alternative representations that can be requested.

- **Self-describing**.  Adding a couple of 'name' and 'explanation' attributes to
  the json helps a lot in explaining the data.  It aids discovery and
  debugging.

- **Resource-based**. The 'normal' part of the URL is for identifying
  resources.  Extra parameters (``?width=100&height=80``) are for small tweaks
  and adjustments.

- **Identify resources, not actions**.  Give every resource a URL, restrict
  the use of verbs.  So not ``/get_document?id=42``, but ``/documents/42``.

To cut to the chase, this is my proposed lizard jdbc url structure.
Everything postfixed with ``_id`` is an id (or slug) that depends on the
actual item being requested::

    /api/
    /api/jdbc_id/
    /api/jdbc_id/filter_id/
    /api/jdbc_id/filter_id/parameter_id/
    /api/jdbc_id/filter_id/parameter_id/location_id/
    /api/jdbc_id/filter_id/parameter_id/location_id/csv/
    /api/jdbc_id/filter_id/parameter_id/location_id/table/
    /api/jdbc_id/filter_id/parameter_id/location_id/table/?period=14
    /api/jdbc_id/filter_id/parameter_id/location_id/png/
    /api/jdbc_id/filter_id/parameter_id/location_id/png/?width=100&height=80

Every call returns json, except for the csv/table/png representations being
requested of the actual filter/parameter/location "end points".

The api/jdbc/filter/parameter resources return a json with a list of items
within it, so ``/api/`` returns a list of available jdbcs, for instance.
Those list items provide the name and url of the jdbcs it points at, see this
partial json example::

    [{"name": "Production FEWS at N&S",
      "url": "http://rijnlandapi.lizardsystem.nl/api/production"},
     {...}]

In this way, it is easy to construct a web interface based on these json
files.  You do not need to know the available IDs beforehand, you can simply
ask the system for the current list.  And requesting the next set of
information is simply a matter of "following the url".

Every json return will have a fixed structure::

    {"info": {"name": "One-line name of current resource",
              "explanation": "Explanation of contents, for programmers"},
     "alternative_representations": [{"type": "csv",
                                      "url": "..."},
                                     {"type": "png",
                                      "url": "..."}],
     "data": [...the actual data, like list of subitems or actual data ...]}

Everything with a ``url`` parameter can also have an ``arguments`` parameter::

    ...
    "url": "....",
    "arguments": {"period": "period in days counted backwards from now",
                  "width": "graph width in pixels"
                  "height": "graph height in pixels"}
    ...


All in all, a call to get a png from the production jdbc, filter 32, parameter
2, location 134, for the last month, would be::

    http://rijnlandapi.lizardsystem.nl/api/production/32/2/134/png/?width=100&height=80&period=31


