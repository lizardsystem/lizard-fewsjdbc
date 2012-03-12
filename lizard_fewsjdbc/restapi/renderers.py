from djangorestframework.renderers import JSONRenderer
from djangorestframework.renderers import JSONPRenderer
from djangorestframework.renderers import DocumentingHTMLRenderer
from djangorestframework.renderers import DocumentingXHTMLRenderer
from djangorestframework.renderers import DocumentingPlainTextRenderer
from djangorestframework.renderers import XMLRenderer

# We subclass the documenting renderers so that we can have our own
# templates.  The templates are passed the view object (and not the
# renderer), so any extra variables we want to use in the templates
# should be defined as variables or methods on the view.


class JdbcDocumentingHTMLRenderer(DocumentingHTMLRenderer):
    template = "lizard_fewsjdbc/restapi.html"


RENDERERS = (JSONRenderer,
             JSONPRenderer,
             JdbcDocumentingHTMLRenderer,
             XMLRenderer)
