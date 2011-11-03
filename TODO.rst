TODO
====

- Crumbs are broken since the switch to lizard-map 3.3 and class based views, because
  the crumbs are in lizard-ui and it doesn't work with class based views yet.

- Figure out a better way to handle timezones.  It is now hardcoded
  that the datetimes we get from jdbc are GMT+1.
