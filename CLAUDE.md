# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal blog and portfolio site at jamie.codes, built with **Zola** (Rust-based static site generator) using the **Apollo** theme (Git submodule at `themes/apollo/`).

## Common Commands

```bash
zola serve              # Local dev server at http://127.0.0.1:1111 with live reload
zola build              # Build static site to public/
zola check              # Validate internal links and config
```

Theme development commands (run from `themes/apollo/`):

```bash
just build              # Build with minification to dist/
just lighthouse         # Run Lighthouse CI audit
bun test                # Run Playwright UI tests
treefmt                 # Auto-format all files
```

## Architecture

- **config.toml** - Site config: base URL, theme selection, taxonomies, nav menu, social links. Overrides/extends `themes/apollo/config.toml` defaults.
- **content/** - Markdown content organized into sections: `posts/`, `projects/`, `talks/`, plus standalone pages like `about.md`. Each section has an `_index.md` for listing configuration.
- **themes/apollo/** - Full theme submodule containing templates (Tera/Jinja2-style), SCSS styles, JS, shortcodes, and Playwright tests. Has its own `CLAUDE.md` with detailed theme docs.
- **static/** - Static assets copied directly to output (includes `CNAME` for GitHub Pages custom domain).

## Deployment

GitHub Actions (`.github/workflows/main.yml`) auto-builds and deploys to `gh-pages` branch on push to `master` using `shalzz/zola-deploy-action`.

## Content Conventions

- Blog posts go in `content/posts/` as Markdown with TOML frontmatter (`+++` delimiters).
- Projects go in `content/projects/`, talks in `content/talks/`.
- Tags are the sole taxonomy (configured in `config.toml`).
- Theme shortcodes available: `image`, `note`, `mermaid`, `character`.

## Key Config Options

The `[extra]` section in `config.toml` controls theme behavior:
- `theme = "toggle"` enables light/dark theme switching
- `socials` array for social media links with icon names
- `menu` array defines nav items with weights for ordering
