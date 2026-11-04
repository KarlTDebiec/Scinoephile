# Local web interfaces

Use Flask, Jinja, and the bundled HTMX asset for local authoring interfaces.
Load optional dependencies through `core.dependencies.web` and construct apps with
[`web.security.create_local_app`](../scinoephile/web/security.py).

- Keep domain routes, templates, and business logic in their existing packages.
- Trust loopback aliases and the explicitly configured bind host. A wildcard bind
  does not authorize arbitrary Host headers; select a concrete host for access
  through a different address or hostname.
- Send the session's `csrf_token` in every mutation form, or use the
  `X-CSRF-Token` header. Reject explicit foreign origins and cross-site requests
  for every method, including GET routes that scan and persist validation results.
  Allow initial browser navigation without origin or fetch-context headers.
- Preserve ordinary POST form actions alongside HTMX attributes. Return the full
  document, or redirect to it, after submissions without HTMX.
- Serve scripts locally with deferred loading. Keep session responses uncached and
  preserve the shared content, framing, and MIME protection headers.
- Test actual app request rejection and valid form submissions, including ordinary
  browser forms without JavaScript. Include template and browser assets in builds.

Adapted from `aXYom32/tools/docs/WEB.md` and its shared local app factory.
