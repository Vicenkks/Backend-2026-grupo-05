"""Swagger conserva el Bearer en memoria."""

import logging

from fastapi.responses import HTMLResponse, Response


class RedactQuery(logging.Filter):
    def filter(self, record):
        # Los enlaces de recuperación contienen credenciales: no registrar queries.
        if isinstance(record.args, tuple) and len(record.args) == 5:
            args = list(record.args)
            args[2] = str(args[2]).split("?", 1)[0]
            record.args = tuple(args)
        return True


def configure_docs(app):
    logging.getLogger("uvicorn.access").addFilter(RedactQuery())

    @app.get("/docs", include_in_schema=False)
    def swagger():
        return HTMLResponse("""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>API Coworking</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head><body><div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script src="/docs/session.js"></script></body></html>""")

    @app.get("/docs/session.js", include_in_schema=False)
    def session_script():
        return Response(
            SWAGGER_SCRIPT,
            media_type="application/javascript",
            headers={"Cache-Control": "no-store"},
        )


SWAGGER_SCRIPT = """
(() => {
  const publicPaths = new Set(['/auth/registro', '/auth/login', '/auth/recuperacion', '/auth/restablecer']);
  window.ui = SwaggerUIBundle({
    url: '/openapi.json', dom_id: '#swagger-ui', deepLinking: true,
    presets: [SwaggerUIBundle.presets.apis], withCredentials: true,
    persistAuthorization: false,
    requestInterceptor: request => {
      const url = new URL(request.url, location.href);
      if (url.origin !== location.origin) return request;
      if (publicPaths.has(url.pathname)) {
        delete request.headers.Authorization;
        delete request.headers.authorization;
      }
      return request;
    },
    responseInterceptor: response => {
      const path = new URL(response.url, location.href).pathname;
      if (response.status >= 200 && response.status < 300) {
        if (['/auth/login', '/auth/refresh'].includes(path)) {
          const data = response.obj || JSON.parse(response.text || response.data);
          if (data.access_token) window.ui.preauthorizeApiKey('HTTPBearer', data.access_token);
        }
        if (['/auth/logout', '/auth/restablecer'].includes(path)) {
          window.ui.authActions.logout(['HTTPBearer']);
        }
      }
      return response;
    }
  });
})();
"""
