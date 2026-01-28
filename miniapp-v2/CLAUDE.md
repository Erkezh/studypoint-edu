# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StudyPoint Miniapp - Educational learning platform for students. Exercises are built as React mini apps (via Claude Artifacts) and embedded in a Vue.js shell.

## Tech Stack

- **Core App**: Vue.js UMD version (loaded directly in index.html)
- **Exercises**: React components with Tailwind CSS and lucide-react icons
- **Communication**: postMessage API between Vue shell and React iframes

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Vue.js Shell (index.html)                      │
│  ┌──────────────────────────────────┬────────┐  │
│  │         Header                   │        │  │
│  ├──────────────────────────────────┤ Score  │  │
│  │                                  │ Stats  │  │
│  │   iframe (React Exercise)        │ Panel  │  │
│  │                                  │        │  │
│  ├──────────────────────────────────┴────────┤  │
│  │         Footer                            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

- **index.html**: Vue.js UMD app with layout (header, footer, iframe center, stats sidebar)
- **exercises.json**: Exercise list fetched by core app
- **exercieses/**: Individual React exercise components loaded in iframe

## Exercise-Shell Communication

React exercises send results to Vue shell via `postMessage`:
- Correct/wrong answer counts
- Exercise completion status
- Vue shell tracks global score and stats

## Exercise Component Pattern

Each exercise component (like `fraction_comparison_app.tsx`):
- Self-contained with problem generation
- Tracks local progress and scoring
- Reports results to parent via postMessage
