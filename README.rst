lizard-fewsjdbc
==========================================

This app is used to view fews-jdbc data sources. The interface looks the same as
fews-unblobbed. Multiple fews-jdbc sources can be configured.


Prerequisities
--------------

- Jdbc2Ei. The app uses Jdbc2Ei to connect to a jdbc server.


Development installation
------------------------

The first time, you'll have to run the "bootstrap" script to set up setuptools
and buildout::

    $> python bootstrap.py

And then run buildout to set everything up::

    $> bin/buildout

(On windows it is called ``bin\buildout.exe``).

You'll have to re-run buildout when you or someone else made a change in
``setup.py`` or ``buildout.cfg``.

The current package is installed as a "development package", so
changes in .py files are automatically available (just like with ``python
setup.py develop``).

If you want to use trunk checkouts of other packages (instead of released
versions), add them as an "svn external" in the ``local_checkouts/`` directory
and add them to the ``develop =`` list in buildout.cfg.

Tests can always be run with ``bin/test`` or ``bin\test.exe``.


Using the djangoapp in a site
-----------------------------

- Add lizard_fewsjdbc to your buildout.cfg. You may need lizard-fewsjdbc's sysegg requirements -
  PIL, matplotlib, pyproj and psycopg2 installed on your system.

- Add lizard_fewsjdbc and lizard_map to the INSTALLED_APPS in your
  settings.

- Optionally set MAP_SETTINGS, DEFAULT_START_DAYS and DEFAULT_END_DAYS
  in your settings. See the lizard_map testsettings for examples.

Make the database tables::

    $> bin/django syncdb

Load some config (optional)::

    $> bin/django loaddata lizard_fewsjdbc

Add some references in your urls.py, i.e. ``(r'^', include('lizard_fewsjdbc.urls'))``.


Prefill cache
-------------

Add a crontab job to your deploy.cfg to run "bin/django
fews_jdbc_cache" every 8 hours. This way visitors of the page
will always get cached contents, which is a huge user experience
boost.

deploy.cfg::

    [fews-jdbc-cronjob]
    recipe = z3c.recipe.usercrontab
    times = * */8 * * *
    command = ${buildout:bin-directory}/django fews_jdbc_cache
