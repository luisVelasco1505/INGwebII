import os

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs')
)

SWAGGER_UI_HTML = """<!doctype html>
<html>
  <head>
    <title>Sistema de Control Veterinario API</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = () => {
        window.ui = SwaggerUIBundle({
          url: '/openapi.yaml',
          dom_id: '#swagger-ui',
        });
      };
    </script>
  </body>
</html>
"""


@api_view(['GET'])
@permission_classes([AllowAny])
def openapi_spec(request):
    with open(os.path.join(DOCS_DIR, 'openapi.yaml'), encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/yaml')


@api_view(['GET'])
@permission_classes([AllowAny])
def swagger_ui(request):
    return HttpResponse(SWAGGER_UI_HTML, content_type='text/html')
