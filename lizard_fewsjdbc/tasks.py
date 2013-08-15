import logging

from celery.task import task
from django.db import transaction

from lizard_task.handler import get_handler
from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.models import CACHE_TIMEOUT
from lizard_fewsjdbc.models import WebRSSource
from lizard_fewsjdbc.cache_fews import FewsJDBCImporter

@task
def test_task(username=None, db_name=None, taskname=None):
    """
    Test task
    """
    handler = get_handler(username=username, taskname=taskname)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(20)

    logger.info('I did my job')
    return 'OK'


def load_parameters(timeout, jdbc_source,
                    tree, url_name, default_url_name, logger):
    params = []
    for item in tree:
        if item["children"]:
            params.extend(
                load_parameters(
                    jdbc_source, item["children"],
                    url_name, default_url_name, logger=logger))
        else:
            logger.debug("Getting named parameters for %s." %
                         (item["id"],))
            if default_url_name:
                parameters = jdbc_source.get_named_parameters(
                    item["id"], ignore_cache=True,
                    cache_timeout=timeout)
            else:
                parameters = jdbc_source.get_named_parameters(
                    item["id"], ignore_cache=True, url_name=url_name,
                    cache_timeout=timeout)
            for p in parameters:
                params.append((item["id"], p["parameterid"]))

    logger.debug("PARAMS: " + str(params))
    return params


@task
def rebuild_jdbc_cache_task(username=None, db_name=None,
                       taskname=None, *args, **options):
    """
    Rebuild filter cache for fewsjdbc.

    Options can be
        timeout
        deep
    """
    handler = get_handler(username=username, taskname=taskname)
    logger = logging.getLogger('rebuild_jdbc_cache')
    logger.addHandler(handler)
    logger.setLevel(20)

    rebuild_jdbc_cache(logger, *args, **options)


def rebuild_jdbc_cache(logger, *args, **options):
    if not logger:
        logger = logging.getLogger('rebuild_jdbc_cache')
        console = logging.StreamHandler()
        logger.addHandler(console)
        logger.setLevel(logging.DEBUG)

    if options.get('timeout'):
        timeout = int(options['timeout'])
    else:
        timeout = CACHE_TIMEOUT
    logger.info("Using a cache timeout of %d seconds." % timeout)

    if options.get('deep', False):
        logger.info("Traversing deep tree.")

    for jdbc_source in JdbcSource.objects.all():
        logger.info('Processing %s ...' % jdbc_source)
        if args:
            default_url_name = False
            if args[0] == 'None':
                url_name = None
            else:
                url_name = args[0]
        else:
            default_url_name = True
        try:
            if default_url_name:
                tree = jdbc_source.get_filter_tree(
                    ignore_cache=True, cache_timeout=timeout)
            else:
                tree = jdbc_source.get_filter_tree(
                    ignore_cache=True, url_name=url_name,
                    cache_timeout=timeout)

            if options.get('deep', False):
                if default_url_name:
                    params = load_parameters(jdbc_source, tree,
                                             default_url_name, logger=logger)
                else:
                    params = load_parameters(jdbc_source, tree, url_name,
                                             default_url_name, logger=logger)
                for filter_id, param_id in params:
                    logger.debug(
                        "Getting locations: %s, %s" %
                        (filter_id, param_id))
                    jdbc_source.get_locations(
                        filter_id, param_id,
                        cache_timeout=timeout)

        except Exception:
            logger.exception('Exception while syncing %s.' % jdbc_source)
    logger.info('Finished.')
    return 'OK'

@transaction.commit_on_success
def rebuild_restws_cache(logger, source_code=None):
    """
    Rebuild fews caches: (filters, locations, parameters, timeseries)

    Raise exception to rollback transaction on error
    """
    
    if logger is None:
        logger = logging.getLogger("tasks.rebuild_restws_cache")

    importer = FewsJDBCImporter(logger)
    importer.remove_all_caches()

    if source_code != None:
        webrs_sources = [WebRSSource.objects.get(code=source_code)]
    else:
        webrs_sources = list(WebRSSource.objects.all())

    for webrs_source in webrs_sources:
        logger.info("Cache source {}".format(webrs_source.code))
        ok = importer.cache_resources(webrs_source)
        if ok == False:
            raise Exception("Error on cache, rollback all changes, "
                            "for info check previous logging")
    

@task
def rebuild_restws_cache_task(username=None, source_code=None,
                       taskname=None, levelno=20):
    """
    Rebuild filter, location, parameter, timeseries cache for fewsjdbc.

    """
    #handler = get_handler(username=username, taskname=taskname)
    #logger = logging.getLogger('rebuild_restws_cache')
    #logger.addHandler(handler)
    #logger.setLevel(levelno)

    rebuild_restws_cache(None, source_code)
