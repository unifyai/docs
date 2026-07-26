# Docs

The public documentation site for Unify, published with [Mintlify](https://mintlify.com).

This is a content repository. Most changes here are prose and MDX, not application
code — but the shared engineering rules below still apply to the tooling and to any
scripts under `tests/`.

## Layout

Navigation and site config live in `mint.json`; every page must be registered there
to appear. Content is `.mdx` grouped by product area:

| Path | Covers |
|---|---|
| `introduction.mdx` | Entry point |
| `learning/` | Conceptual guides |
| `integrations/` | Third-party app connections |
| `communication/` | Phone, SMS, email channels |
| `teams/`, `tasks/`, `canvas/` | Product surfaces |
| `hiring/` | Assistant hiring flow |
| `local-deployment/` | Running the stack locally |
| `their-computer/` | Assistant desktop |
| `images/` | Screenshots and diagrams |

## Local preview

```bash
docker build -t docs:latest -f Dockerfile .
docker run -v .:/docs -p 3000:3000 docs:latest
```

The site serves at `http://localhost:3000`. Restart the existing container rather
than creating a new one — `mintlify dev` re-downloads the framework on every fresh
container, which is slow.

```bash
docker restart <container-id>
```

## Writing conventions

- Register every new page in `mint.json`, or it will not be reachable.
- Keep code samples runnable against the hosted Orchestra backend
  (`ORCHESTRA_URL`, default `https://api.unify.ai/v0`). This is public-facing
  documentation for the open-source path — do not document the private
  full-local self-host stack here; that lives in `unify-deploy/selfhost/`.
- Never put real API keys, tokens, customer names, or PII in examples. Use
  placeholders (`@example.com`, fictional `555-01xx`).
- Screenshots go in `images/`; reference them with relative paths.

## Relationship to other repos

Documentation describes the behaviour implemented in `unify` (runtime), `unisdk`
(Python SDK), and `unillm` (LLM layer), and the hosted surfaces in `orchestra` and
`console`. When behaviour changes in those repos, the corresponding page here needs
updating in the same change — a doc that describes a shipped API incorrectly is
worse than no doc.
