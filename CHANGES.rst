
Changelog of lizard-fewsjdbc
============================


1.34 (unreleased)
-----------------

- Nothing changed yet.


1.33 (2012-05-15)
-----------------

- Add MANIFEST.in


1.32 (2012-05-15)
-----------------

- Create tasks.py and move fews_jdbc_cache management command to it.


1.31 (2012-03-20)
-----------------

- Removed 'ignore_cache=True' from filter URLs created while the
  ignore cache variable is True. Just that the cache is currently
  being refreshed doesn't mean that the newly cached URLs should
  ignore the cache.

- Fixed bug in fews_jdbc_cache command where it would crash if -d was
  used without an url_name.

1.30 (2012-03-13)
-----------------

- Improved functionality of start_end_dates in the REST API:
  - Removed padding from start and end time
  - 'end' date now gives data up to and including 23:59 on that date

- Added a command to show filters and parameters of a given jdbc
  source.


1.29 (2012-03-12)
-----------------

- Changed the layout and titles of the REST API pages.


1.28 (2012-03-09)
-----------------

- Added two more arguments to the fews_jdbc_cache command:
  -d / --deep : Do a "deep" tree traversal, in the sense that not only
                filters are cached, but parameters and locations too.
  -t / --timeout : Give the duration that values will be kept in the
                   cache, in seconds (the default is currently 8 hours).


1.27 (2012-03-07)
-----------------

- Added optional argument to the fews_jdbc_cache management command.
  Without it, the command creates a filtertree with URLs in it to the
  'lizard_fewsjdbc.jdbc_source' view, but if that's not available the
  command would crash. Give argument 'None' to turn the URLs off, or
  a name to another view.


1.26 (2012-01-17)
-----------------

- Created (the start of) a new REST API using djangorestframework (in
  lizard_fewsjdbc/restapi/).

- Added support for jdbc sources in breadcrumbs

1.25 (2012-01-04)
-----------------

- Hack that seems to fix an issue with location() in layers.py


1.24 (2011-12-21)
-----------------

- Made parameters have the css class 'selected' if they are already
  present in the workspace.


1.23 (2011-12-20)
-----------------

- Made it possible to scale graphs manually.

- Made sure legend is always visible.


1.22 (2011-12-19)
-----------------

- Added parameter and filter names to popup.


1.21 (2011-11-04)
-----------------

- Upgraded to lizard-map 3.3.

- Turned views into class based views, changed templates accordingly.

- Changed buildout.cfg to work with the latest KGS (currently including lizard-ui 3.6, used to be pinned to 2.1.5)

1.20 (2011-09-20)
-----------------

- Raising WorkspaceItemError if the jdbc source doesn't exist. This way,
  existing lizard sessions don't get stuck with an 'error 500' if a jdbc
  source is renamed or removed.


1.19 (2011-09-16)
-----------------

- Fixed timezone bug in Jdbc2Ei and adapted JdbcSource.get_timeseries
  accordingly. https://office.nelen-schuurmans.nl/trac/ticket/3231


1.18 (2011-08-30)
-----------------

- Added adapter_class as an option to the jdbc_source view. This is
  done for reusability of the view.


1.17 (2011-08-17)
-----------------

- Fixed API timeseries request #3156.

- Added version dependency to lizard_map and lizard_ui.

- Added option for admin IconStyles.


1.16 (2011-08-04)
-----------------

- Added min/max/avg/label/horizontal lines to adapter.image function.

- When clicking on a parent filter, the result is now the listing of
  the parameters from filters below. #3029.

- Added IconStyle model and migration. Icons are now configurable. It
  will revert to a default when nothing is configurated.

Note: Clear cache when upgrading to this tag.


1.15 (2011-07-26)
-----------------

- Implemented ignore_cache in get_named_parameters and
  get_parameter_name. Previously the functions ignored the
  ignore_cache parameter.

- Removed force_legend_below and border in adapter.image graph.


1.14 (2011-06-16)
-----------------

- Added try/except in adapter.layer to prevent the function from crashing.


1.13 (2011-06-10)
-----------------

- Showing legend in the graph (plus, the legend is always below the graph).

- Using the location name in the legend.

- Limiting the number of search results to three.


1.12 (2011-06-03)
-----------------

- Depending on lizard-ui > 1.64 as that allows us to not pass along the full
  filter tree when viewing one specific filter item: it saves on the transfer
  time.

- Requiring lizard-map >= 1.80 as we don't have to specify click/hover map
  javascript handlers anymore. And hovering is switched off by default now.

- Removed unused imports.


1.11 (2011-04-21)
-----------------

- Removed unnecessary workspace_manager and date_range_form stuff. It
  is also incompatible with map >= 1.71.


1.10 (2011-03-17)
-----------------

- Corrected faulty migration step (filter_tree_root column was
  inexplicably missing).

- Added south so that the tests also run the migrations, which ensures
  that inexplicably missing migrations at least result in a very
  opinionated reply from the test runner.


1.9.1 (2011-03-10)
------------------

- Added robustness to management fews_jdbc_cache command.


1.9 (2011-03-09)
----------------

- Enabled the 'ignore_cache' option.

- Added management commands to pre-fill cache (user experience boost).

- Added initial migration.


1.8 (2011-02-21)
----------------

- Returning 404s now when there's no data to display for timeseries
  (html, csv, json, png).


1.7 (2011-02-17)
----------------

- Removed mandatory authentication from our experiemental REST api.


1.6 (2011-02-16)
----------------

- When using "period" to select date ranges in the REST api, we count
  from "now" instead of "0:00 today".


1.5 (2011-02-16)
----------------

- Using latest lizard-map with a better date range handling.


1.4 (2011-02-14)
----------------

- Swapped csv emitter for a csv handler: we cannot set the necessary
  response headers in an emitter.


1.3 (2011-02-10)
----------------

- Added sphinx documentation.  (See
  http://doc.lizardsystem.nl/libs/lizard-fewsjdbc/ ).

- Showing parameter name in csv/html column header.

- Making explicit that the extracted datetime is GMT+1.

- Added 'period' parameter: the start/end dates are set to -period
  days till now.


1.2 (2011-02-08)
----------------

- Added height/width support to png api call.


1.1 (2011-02-08)
----------------

- Adding better error handling to jdbc queries: they raise errors
  right away now instead of returning -1 or -2 and checking later on
  in the code.

- Supporting date range setting.

- Added csv/html/png output.

- Added implementation of lizard-map's REST api for jdbc sources,
  filters, parameters and locations.

- Added ``.get_locations()`` method to jdbc source model (with the
  rest of the related get_something methods) instead of keeping it in
  the adapter.


1.0.1 (2011-02-02)
------------------

- Added crumbs_prepend (see lizard_ui).


1.0 (2011-01-13)
----------------

- Fixed some points not showing. Working around Mapnik bug #402. Needs
  lizard-map 1.39 or higher.

- Implemented adapter.extent.


0.9.2 (2010-12-09)
------------------

- Fixed not showing all parameters.


0.9.1 (2010-12-08)
------------------

- Bugfix moving operations.


0.9 (2010-12-08)
----------------

- Moved list operations to lizard_map (1.27).

- Added filter_tree_root. The filter_tree_root takes a filter_id as a
  root and loads the tree from that point. Use only if not using
  usecustomfilter.


0.8 (2010-11-10)
----------------

- Bugfix accordion.

- Add tests, make tests independent of external data source.


0.7 (2010-10-18)
----------------

- Bugfix using iso8601.


0.6 (2010-10-18)
----------------

- Change datetime conversion from timetuple to iso8601 parsing
  (timetuple does not always exist).


0.5 (2010-10-15)
----------------

- Use lizard-ui 1.21.


0.4 (2010-10-15)
----------------

- Added option ignore_cache in fews_jdbc page.


0.3 (2010-10-15)
----------------

- Added usecustomfilter option.

- Update fixtures.


0.2 (2010-10-15)
----------------

- Pinned lizard-map and lizard-ui.


0.1 (2010-10-15)
----------------

- Initial library skeleton created by nensskel.  [Jack]

- Added model for Jdbc source.

- Frontpage shows list of Jdbc sources.

- Added tests.

- Each Jdbc source has an own page, where workspace items can be used.

- Basic adapter for Jdbc source implemented: layer, image, values, ...
