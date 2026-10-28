# Web tools

Use **Flask + Jinja + HTMX** for local authoring interfaces. Install the optional
`web` extra and serve on `127.0.0.1` through an installed CLI command.

- Reuse shared web infrastructure where available for host, origin,
  CSRF, safe external links and response-header configuration. Shared HTMX helpers
  identify fragment requests (excluding history restoration) and build response headers.
- Keep routes, templates and static assets in their domain package. Keep business
  logic independent of HTTP and load optional dependencies lazily.
- Render HTML with Jinja and support core functionality through ordinary links
  and forms without JavaScript. Use HTMX and minimal custom JavaScript for
  progressive enhancement. Bundle pinned browser dependencies with their licenses.
  Serve shared HTMX separately from domain-owned assets;
  load it with a deferred script tag.
- Run expensive operations in workers. The music app uses one native EventSource
  connection per document to trigger HTMX fragment refreshes when state changes.
  Preserve active controls and unsaved input, retaining deferred refreshes until
  interaction ends. Keep the connection outside swapped content and close it on
  page exit. Revision notifications coalesce changes; reconnecting refreshes the
  latest state instead of replaying old HTML. Idle SSE comments maintain the
  connection without polling application state. Bound streams (eight per server)
  and reserve Waitress threads for ordinary requests (sixteen total).
- Validate inputs and artifact paths in domain routes. Submit mutations with the
  session CSRF token in a form field or request header.
- Test core flows with JavaScript disabled and routes with Flask's test client. Run the
  [Python checks](STYLE.md). Include templates and static assets
  in package builds.

## Browser source conventions

Use JSDoc `@file` comments for first-party script ownership and function comments
for behavior and lifecycle constraints. Document named handler parameters with
`@param` and meaningful returned values with `@returns`; use `@type` for persistent
collections or non-obvious state. Anonymous event callbacks need comments only
when their intent is not apparent. Keep DOM identifiers and event names consistent
with templates, and use delegated handlers or repeat-safe initialization after
HTMX/history swaps. Weak collections avoid retaining detached controls.

Use classes for presentation-only hooks, including confirmation states. Reserve
`data-*` attributes for JavaScript hooks, application values and state; native
attributes such as `disabled` and `aria-pressed` remain the source of truth for
their corresponding states.

Group CSS by component, nesting descendant, state and responsive rules beside their
owner. Combine identical selector groups without changing cascade order or
specificity. Keep icons as individual SVGs under the owning static directory;
reference them with `<use>` for theme color inheritance, and provide accessible
names on the surrounding controls. Preserve upstream licenses and adaptation notes.

## Scinoephile conventions

Adapted from `aXYom32/tools/docs/WEB.md`. The browser source conventions above
apply to new and edited web code; the music app's SSE/thread counts describe its
workflow, not a requirement to add background workers or SSE to every interface.
Use the existing serving infrastructure unless the task requires changing it.

- Prefer native elements and their state: details/summary for disclosures, forms
  for edits, and real inputs for verification. Do not replace native controls
  after rendering to simulate an accordion or toggle.
- Keep HTML semantic and shallow. Use a wrapper only when it owns layout, state,
  accessibility, or an HTMX swap target. Remove empty labels and redundant status
  badges. Prefer element and native attribute selectors within a component;
  add a class only when it expresses a distinct presentation responsibility.
- Keep base HTML usable before enhancement loads or if it fails. Do not hide
  editable text until JavaScript paints an overlay. CSS-only state and native
  controls should handle visibility and toggles where possible.
- Preserve unrelated drafts during fragment updates. Review the ordinary form
  path as well as HTMX saves, filtering, history restoration, and lazy loading.
- Keep domain assets under the domain package, with a separate shared vendor
  asset directory. Include nested icon files and licenses in package builds.