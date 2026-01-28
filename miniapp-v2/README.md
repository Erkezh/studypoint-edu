# StudyPoint Miniapp

A learning platform that loads React exercises from Claude Artifacts directly - no build step required.

## Quick Start

```bash
# Install serve globally (one time)
npm install -g serve

# Run the app
cd /Users/timurjunussov/Dev/studypoint/miniapp
serve
```

Open http://localhost:3000 in your browser.

## Adding New Exercises

1. Create exercise in **Claude Artifacts** (React)
2. Copy the code
3. Save as `.tsx` file in `exercieses/` folder
4. Add to exercises list in `index.html`:

```javascript
const exercises = ref([
  { id: 'fraction-comparison', name: 'Fraction Comparison', file: 'exercieses/fraction_comparison_app.tsx' },
  { id: 'new-exercise', name: 'New Exercise', file: 'exercieses/new_exercise.tsx' }  // Add here
])
```

That's it! The TSX file is loaded and transformed automatically.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  index.html (Vue.js Shell)                              │
│                                                         │
│  ┌─────────────────────────────────────┬─────────────┐  │
│  │            Header                   │             │  │
│  ├─────────────────────────────────────┤   Stats     │  │
│  │                                     │   Panel     │  │
│  │   <iframe srcdoc="...">             │             │  │
│  │     Transformed React Exercise      │  Correct: 5 │  │
│  │                                     │  Wrong: 2   │  │
│  │                                     │  Total: 7   │  │
│  │                                     │             │  │
│  ├─────────────────────────────────────┤  Exercise   │  │
│  │            Footer                   │  List       │  │
│  └─────────────────────────────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### How It Works

1. Vue shell fetches `.tsx` file
2. **Transformer** converts Claude Artifacts code to browser-ready:
   - `import { useState } from 'react'` → `const { useState } = React`
   - `import { Check, X } from 'lucide-react'` → uses SVG shim
   - `export default Component` → removed
   - Injects `postMessage` into `handleSubmit` for score tracking
3. Transformed code injected into iframe via `srcdoc`
4. React app runs with Babel (in-browser transpilation)

### Communication (postMessage)

```
┌──────────────────┐       postMessage        ┌──────────────────┐
│  React Exercise  │  ──────────────────►     │    Vue Shell     │
│  (iframe)        │  { type: 'exercise-      │  (parent)        │
│                  │    result', correct }    │                  │
└──────────────────┘                          └──────────────────┘
```

The transformer automatically injects `postMessage` into `handleSubmit`:
```javascript
window.parent.postMessage({ type: 'exercise-result', correct: __correct }, '*');
```

## File Structure

```
miniapp/
├── index.html                           # Vue.js shell + TSX transformer
├── exercieses/
│   └── fraction_comparison_app.tsx      # React exercise (unchanged from Claude Artifacts)
├── README.md
└── CLAUDE.md
```

## Why This Architecture?

### 1. Zero Build Step
Copy-paste from Claude Artifacts → save → works. No webpack, no vite, no npm install.

### 2. Isolation
Each exercise runs in its own iframe sandbox. Crashes don't affect the main app.

### 3. Technology Independence
Shell is Vue.js, exercises are React. They coexist without conflicts.

### 4. Future-Ready
When backend is ready, just change `file:` to API URL - transformer works the same.

## Supported Imports

The transformer handles these imports automatically:

| Import | Transformed to |
|--------|----------------|
| `import React, { useState, useEffect } from 'react'` | `const { useState, useEffect } = React` |
| `import { Check, X, Star, ... } from 'lucide-react'` | SVG icon shim |

### Adding More Lucide Icons

If an exercise uses icons not in the shim, add them to `LUCIDE_SHIM` in `index.html`. Current icons: `RefreshCw`, `Check`, `X`, `ChevronLeft`, `ChevronRight`, `Star`.

## Future: Backend Integration

When backend is ready:

```javascript
// Instead of local files
const exercises = ref([
  { id: 'fraction', name: 'Fractions', file: 'https://api.studypoint.com/exercises/fraction' }
])
```

The Vue shell will fetch TSX code from API, transform it, and run - same flow.
