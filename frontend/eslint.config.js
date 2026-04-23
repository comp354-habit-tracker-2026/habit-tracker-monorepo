import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import checkFile from 'eslint-plugin-check-file';
import { defineConfig, globalIgnores } from 'eslint/config';

export default defineConfig([
  globalIgnores([
    'dist',
    'cypress/videos',
    'cypress/screenshots',
    'cypress/downloads',
    'src/App.tsx',
  ]),
  js.configs.recommended,
  tseslint.configs.recommended,
  reactHooks.configs.flat.recommended,
  reactRefresh.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      'check-file': checkFile,
    },
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      // Enforce kebab-case for all TypeScript/TSX files
      'check-file/filename-naming-convention': [
        'error',
        {
          '**/*.{ts,tsx}': 'KEBAB_CASE',
        },
        {
          // Allow middle extensions like .test.ts, .stories.tsx
          ignoreMiddleExtensions: true,
        },
      ],
      // Enforce kebab-case for all folders under src (except __tests__)
      'check-file/folder-naming-convention': [
        'error',
        {
          'src/**/!(__tests__)': 'KEBAB_CASE',
        },
      ],
    },
  },
  {
    files: ['cypress/**/*.ts', 'cypress.config.ts'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.cypress,
      },
    },
  },
]);
