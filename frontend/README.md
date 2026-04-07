# Habit Tracker – Frontend

[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-7-purple?logo=vite)](https://vite.dev)

This app is a React + TypeScript + Vite single-page application structured around the
**[Bulletproof React](https://github.com/alan2207/bulletproof-react)** architecture guide.

> **Important:** Bulletproof React is not a framework or a template — it is an _opinionated_ guide
> that prescribes a particular way of organising code. The rules here exist to keep a codebase
> maintainable when it is worked on by many students simultaneously. You are not forced to follow
> every rule exactly, but every deliberate deviation should be discussed with the team first and
> documented so the codebase stays consistent.

---

## Why this structure?

When more than a handful of people contribute to the same repository, small inconsistencies
compound quickly:

- Merge conflicts in sprawling flat folders
- Hidden circular imports between features
- Inconsistent naming that slows code review
- No shared mental model of where a new file should live

The Bulletproof React approach solves these problems by enforcing clear boundaries:

```
shared (utils, types, hooks, components)
  ↓
features (habits, auth, …)
  ↓
app (routes, providers)
```

Code flows in **one direction only**. A feature must _never_ import from another feature.
Shared logic belongs in `src/components/`, `src/hooks/`, `src/lib/`, `src/utils/`, or `src/types/`.

---

## Folder structure

```
src/
├── app/                  # Application layer (routes, provider, router)
│   ├── routes/
│   │   └── app/          # Authenticated /app/* routes
│   ├── index.tsx         # Composes AppProvider + AppRouter
│   ├── provider.tsx      # Global providers (QueryClient, ErrorBoundary, …)
│   └── router.tsx        # createBrowserRouter definition
│
├── assets/               # Static files (images, fonts)
│
├── components/           # Shared UI used across the whole app
│   ├── errors/           # Error-boundary fallback components
│   └── layouts/          # Shared page layout wrappers
│
├── config/               # Typed environment variables and route paths
│   ├── env.ts            # Zod-validated env config (fails fast on a bad .env)
│   └── paths.ts          # Central route-path helpers — no hard-coded strings
│
├── environments/         # .env.dev / .env.prod loaded by Vite
│
├── features/             # Feature-based modules — one folder per domain concept
│   └── habits/
│       ├── api/          # React Query query/mutation hooks + query-key factories
│       ├── components/   # Components scoped to this feature only
│       ├── hooks/        # Non-API hooks scoped to this feature
│       └── types/        # Zod schemas + TypeScript types for this feature
│
├── hooks/                # Shared hooks used across multiple features
├── lib/                  # Pre-configured third-party library wrappers
│   ├── api-client.ts     # Axios instance with base URL + error interceptors
│   └── react-query.ts    # Global React Query defaults
│
├── stores/               # Global Zustand (or similar) stores for UI state
├── types/                # Shared TypeScript types (API response shapes, etc.)
└── utils/                # Pure utility functions (cn, formatDate, …)
```

---

## Quick start

```bash
# Install dependencies
npm install

# Start the dev server (loads src/environments/.env.dev)
npm run dev
```

---

## Environment variables

Vite loads different env files depending on the `--mode` flag passed to it.
All env files live in `src/environments/` (configured via `envDir` in [vite.config.ts](vite.config.ts)).

| File                         | Loaded by                            | Purpose                      |
| ---------------------------- | ------------------------------------ | ---------------------------- |
| `src/environments/.env.dev`  | `--mode dev` (dev server, dev build) | Local development values     |
| `src/environments/.env.prod` | `--mode prod` (production build)     | Production / deployed values |

**Every variable must be prefixed with `VITE_`** so Vite exposes it to the browser bundle.
All variables are validated at startup via Zod in [src/config/env.ts](src/config/env.ts) — the
app throws immediately if a required variable is missing or has the wrong type.

```dotenv
# src/environments/.env.dev
VITE_ENV=dev
VITE_BACKEND_URL=http://localhost:8080
```

```dotenv
# src/environments/.env.prod
VITE_ENV=prod
VITE_BACKEND_URL=https://api.yourapp.com
```

> **Never commit real secrets to these files.** Use environment secrets in your CI/CD. To add secrets contact the DevOps and QA team to inject secrets in the runtime environment. Any sensitive or secret keys should only be handled in the backend as they can be decompiled in the frontend.
> pipeline for values that must not be in source control.

---

## Available scripts

| Script                 | Mode   | Description                                        |
| ---------------------- | ------ | -------------------------------------------------- |
| `npm run dev`          | `dev`  | Start Vite dev server with `.env.dev`              |
| `npm run build`        | `prod` | Type-check + build for production with `.env.prod` |
| `npm run build:dev`    | `dev`  | Build with `.env.dev` (useful for staging/testing) |
| `npm run preview`      | `prod` | Preview the production build locally               |
| `npm run preview:dev`  | `dev`  | Preview the dev build locally                      |
| `npm run typecheck`    | —      | Run `tsc --noEmit` without bundling                |
| `npm run lint`         | —      | Run ESLint across all source files                 |
| `npm run lint:fix`     | —      | Auto-fix ESLint issues                             |
| `npm run format`       | —      | Prettier-format all `src/**/*.{ts,tsx,css}` files  |
| `npm run format:check` | —      | Check formatting without writing changes (for CI)  |
| `npm run cypress:open` | —      | Open Cypress interactive test runner               |
| `npm run cypress:ci`   | `dev`  | Start dev server and run Cypress headlessly        |

---

## Coding standards

This project enforces the following standards automatically. CI will reject any code that
violates them. **Fix issues locally before pushing.**

### ESLint

| Rule                                    | What it catches                                                            |
| --------------------------------------- | -------------------------------------------------------------------------- |
| `check-file/filename-naming-convention` | Files must be **kebab-case** (`use-disclosure.ts`, not `useDisclosure.ts`) |
| `check-file/folder-naming-convention`   | Folders under `src/` must be **kebab-case**                                |
| `eslint-plugin-react-hooks`             | Violations of the Rules of Hooks                                           |
| `typescript-eslint` recommended         | Common TypeScript mistakes                                                 |

### Prettier

Formatting is handled by Prettier — never adjust spacing, quotes, or indentation manually.
The config lives in `.prettierrc`. CI runs `npm run format:check` and will fail if the output
differs from the committed files.

### TypeScript

Strict mode is enabled. Avoid `any`; use `unknown` and narrow types explicitly.
`noUnusedLocals` and `noUnusedParameters` are on, so unused imports and variables are
compile errors.

### Import direction (feature isolation)

Features must **not** import from each other:

```ts
// ✗ WRONG — inside src/features/habits/
import { useUser } from '@/features/auth/api/get-user';

// ✓ CORRECT — extract to shared layer instead
import { useUser } from '@/lib/auth';
```

If two features share something, move it to `src/lib/`, `src/hooks/`, `src/utils/`, or
`src/types/`.

---

## Catch issues before CI — install the recommended extensions

CI will refuse to merge code that breaks any ESLint rule or has incorrect formatting.
**Surface errors directly in your editor** so you never have to wait for CI to tell you
something is wrong.

### VS Code

1. Open the Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`)
2. Install the following extensions:

   | Extension                     | ID                       | Purpose                                                |
   | ----------------------------- | ------------------------ | ------------------------------------------------------ |
   | **ESLint**                    | `dbaeumer.vscode-eslint` | Red squiggles for ESLint errors inline                 |
   | **Prettier – Code formatter** | `esbenp.prettier-vscode` | Auto-format on save                                    |
   | **Error Lens**                | `usernamehw.errorlens`   | Error messages shown inline next to the offending line |

3. The `.vscode/extensions.json` file in this repo lists all three. When you open the project,
   VS Code will prompt: _"Do you want to install the recommended extensions for this repository?"_
   — click **Install All**.

4. `.vscode/settings.json` enables **format on save** and **ESLint auto-fix on save**
   automatically — no manual configuration required.

> Without the ESLint extension, you will only discover rule violations when CI runs.
> That adds an unnecessary delay to every pull request.

### JetBrains IDEs (IntelliJ IDEA / WebStorm)

1. **Settings → Languages & Frameworks → JavaScript → ESLint**
   → select **Automatic ESLint configuration**
   → enable **Run eslint --fix on save**
2. **Settings → Languages & Frameworks → JavaScript → Prettier**
   → enable **On 'Reformat Code' action** and **On save**

---

## Adding a new feature

1. Create `src/features/<feature-name>/` and add only the sub-folders you need (`api/`,
   `components/`, `types/`, `hooks/`).
2. Define Zod schemas and TypeScript types in `types/`.
3. Add API hooks in `api/` using `queryOptions` + a named `useXxx` export.
4. Build UI in `components/` — keep components small and focused on one thing.
5. Add a route file in `src/app/routes/app/<feature>.tsx` using a default export.
6. Register the route (with `lazy()`) in `src/app/router.tsx`.
7. Add path helpers in `src/config/paths.ts`.

---

## Before opening a pull request

Work through this checklist **locally** before pushing. Catching problems here is faster
than waiting for CI to fail on someone else's machine.

- [ ] `npm run typecheck` passes with no errors
- [ ] `npm run lint` passes with no errors
- [ ] `npm run format:check` passes (or run `npm run format` to fix automatically)
- [ ] Feature works as expected in the local dev server (`npm run dev`)
- [ ] **Run the project in Docker and verify your feature works in the containerised environment** (see below)
- [ ] Cypress tests pass (`npm run cypress:run`) or new tests have been added for the feature

### Testing in Docker before opening a PR

The app is deployed as a Docker container. Behaviour can differ between your local Node
environment and the container (missing env vars, path issues, port bindings). **Always
spin up the container at least once before marking your PR as ready for review.**

```bash
docker compose up --build
```

This uses [docker-compose.yml](docker-compose.yml), which:

- Builds the image from the local `Dockerfile`
- Passes `BUILD_MODE=development` as a build arg
- Binds the container on **port 3000** → open [http://localhost:3000](http://localhost:3000)
- Mounts `./src` into the container so source changes are reflected without a full rebuild

To stop the container:

```bash
docker compose down
```

> If the app fails to start inside Docker but works locally, check that all required
> `VITE_*` variables are present in `src/environments/.env.dev` — the Zod validation
> in `src/config/env.ts` will print exactly which variables are missing.

---

## Further reading

- [Bulletproof React — Project Structure](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md)
- [Bulletproof React — Project Standards](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-standards.md)
- [Bulletproof React — State Management](https://github.com/alan2207/bulletproof-react/blob/master/docs/state-management.md)
- [Bulletproof React — API Layer](https://github.com/alan2207/bulletproof-react/blob/master/docs/api-layer.md)
- [Bulletproof React — Components & Styling](https://github.com/alan2207/bulletproof-react/blob/master/docs/components-and-styling.md)
- [Bulletproof React — Testing](https://github.com/alan2207/bulletproof-react/blob/master/docs/testing.md)
- [Bulletproof React — Error Handling](https://github.com/alan2207/bulletproof-react/blob/master/docs/error-handling.md)
- [TanStack Query docs](https://tanstack.com/query/latest)
- [React Router docs](https://reactrouter.com)
- [Zod docs](https://zod.dev)
