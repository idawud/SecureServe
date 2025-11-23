# SecureServe — Landing Page

This folder contains a small static landing site and a developer sandbox.

Files:
- `index.html` — main landing page
- `sandbox.html` — interactive mock sandbox for core endpoints
- `styles.css` — site styles
- `scripts.js` — sandbox JS
- `assets/` — SVG logo and architecture diagram

## Local Development

Serve the landing page locally:

```bash
# Option 1: Python built-in server (no dependencies)
python3 -m http.server --directory landing-page 8000
# Then open: http://localhost:8000

# Option 2: Node.js simple-http-server (if installed)
npx http-server landing-page -p 8000

# Option 3: Live reload with Node.js serve (good for development)
npm install -g serve
serve landing-page -p 8000
```

The site is fully static HTML/CSS/JS — no build step required. All endpoints in the sandbox are client-side mocked.

Deploy to GitHub Pages (two simple options):

1. Use `docs/` folder
- Copy `landing-page/*` into `docs/` and set GitHub Pages source to `main` branch `/docs` folder.

2. Use `gh-pages` branch with `gh-pages` npm package
- Add `gh-pages` dev dependency and a `deploy` script that copies `landing-page` to the published branch. Example scripts in the project root `package.json`:

```json
"scripts":{
  "deploy": "gh-pages -d landing-page -b gh-pages"
}
```

No build step is required for this static site.
