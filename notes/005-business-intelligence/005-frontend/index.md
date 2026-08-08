---
title: Frontend
---
As someone with zero frontend experience, the following is a note so that I get a grasp on the concepts. It feels like the frontend ecosystem and Javascript as a whole feels chaotic (compared to Python).

## The Core Stack

Everything in JavaScript relies on two core layers:

- Language: JavaScript / TypeScript
- Runtime: Node.js (or Bun/Deno)
	- The runtime allows JavaScript to run outside the browser (on your terminal/server) to run build tools, dev servers, or backend scripts.

## The UI Frameworks

These are frontend libraries that handle component rendering and state management. These replace raw HTML/JS with reactive components.

- React: The most popular library, which uses JSX (mixing HTML inside JavaScript functions). It relies on explicit hooks (useState) to track updates.
- Vue (or Vue.js): It uses Single-File Components (.vue files) separating `HTML <template>`, `JS <script>`, and `CSS <style>`. 
- 