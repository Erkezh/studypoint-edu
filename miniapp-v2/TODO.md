This is learning application for students, all exercieses will be done via Claude Artifactcs as react mini apps
Core app will be Vue.js umd version, 
- index.html UMD vue.js version which loads react app inside iframe in same page,
- core app has layout header, footer, and center part is iframe, right side is global score and stats ( home much correct/wrong and total)
- react app should commuticate via postMessage what execercies answred correctly, we should move to next js
- list of apps should be stored as separate exercises.json file and fetched