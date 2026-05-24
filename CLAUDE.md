# Developer Guidelines for Rithvik Foods

## Run & Development Commands

Since this is a static HTML/CSS/JavaScript project, it runs directly in any modern browser.

### Local Development Server
To run a local server for testing checkout flow, local storage, and asset loading:
```bash
# Using Python (standard)
python -m http.server 8000

# Using Node.js (if installed)
npx serve .
```

### Image Optimization
To optimize new product images (PNG/JPG) to WebP format for fast web delivery:
```bash
python optimize_images.py
```

## Technology Stack & Guidelines

- **HTML**: Standard HTML5 semantic elements. Ensure unique IDs for all interactive elements to make automated testing easier.
- **CSS**: Vanilla CSS only (located in `main.css`). Use HSL or hex variable tokens for colors. Avoid Tailwind CSS unless explicitly requested.
- **JS**: Vanilla ES6 JavaScript embedded in `index.html` (or separate script files if the codebase expands).
  - Use `camelCase` for variable and function names.
  - Use `escapeHTML` when rendering user-generated content or items from local storage to prevent XSS.
  - Ensure try-catch protection when working with `localStorage`.

## Deployment
- Pushing to the `main` branch automatically deploys to the hosting platform (configured for Netlify or GitHub Pages).
- Always ensure assets are compressed and pages load in under 1 second.
