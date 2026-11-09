# Web interfaces

Use these conventions for new and revised local web editors. The
[subtitle audit editor](../scinoephile/web/audit_review/) is the reference
implementation.

## Application structure

- Serve Flask, Jinja, and HTMX editors through a CLI command on the configured
  local address. Use the [shared app factory](../scinoephile/web/security.py)
  for host and origin checks and response headers. Protect edits from both
  ordinary forms and HTMX with the session CSRF token.
- Keep routes, templates, and editor-specific assets in their domain package.
  Keep workflow logic independent of HTTP and load optional dependencies lazily.
- Run expensive work outside request handlers. Use
  [BackgroundJob](../scinoephile/web/jobs.py) for work that reports progress.
  Refresh the progress fragment without replacing active controls or unsaved input.
- Store editor progress separately from shared training data. Use row versions
  to reject stale edits and coordinate writes to shared files. Confirm reruns
  that can replace saved edits.

## HTML and CSS

- Make core editing work through ordinary links and forms. Give forms a method,
  an action, labeled fields, and submit controls. Redirect after successful
  native submissions and return fragments for HTMX updates.
- Render headings, disclosure controls, and icons in place on the server. Use
  semantic elements and add wrappers when the layout or document structure needs
  them.
- Group CSS by component. Keep state and responsive rules next to their
  component, and reuse shared styles for typography, colors, controls, and toolbars.
- Use classes for styling and `data-*` for application data and JavaScript hooks.
  Reflect control state in attributes such as `disabled` and `aria-pressed`.
- Keep icons as individual SVG files referenced with `<use>`. Give icon-only
  controls accessible names and preserve upstream licenses and adaptation notes.

## JavaScript and checks

- Use HTMX for requests and fragment swaps. Use custom JavaScript for enhancements
  such as keyboard shortcuts and draft feedback. Document first-party scripts
  with JSDoc and make control setup safe to repeat after swaps and history restores.
- Render only the rows the current view needs. Keep expensive per-row work out of
  summary counts.
- Use the same checks as CI for [Jinja HTML](../.github/workflows/html.yml) and
  [JavaScript](../.github/workflows/javascript.yml).
- Test core edits without JavaScript and cover persistence, stale updates, and
  filters. Include templates, static assets, and pinned browser dependencies with
  their licenses in package builds.

Adapted from aXYom32's `tools/docs/WEB.md`.
