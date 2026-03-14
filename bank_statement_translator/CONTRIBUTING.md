# Contributing

Thanks for contributing.

## Development Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` if you need to run OCR or API-backed translation.

## Common Commands

```bash
make test
make lint
make format
make check
```

## Project Guidelines

- Keep changes small and focused.
- Prefer clear module boundaries over clever abstractions.
- Preserve current behavior unless the change explicitly targets a bug fix.
- Add or update tests when changing parsing, glossary, translation, or export logic.
- Keep readable term dictionaries separate from legacy compatibility mappings.

## Pull Request Checklist

- Tests pass locally
- New behavior is covered by tests when practical
- README or docs are updated if usage changed
- No generated files or local secrets are included
