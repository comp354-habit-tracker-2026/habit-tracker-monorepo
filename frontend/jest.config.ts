import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "jsdom",

  roots: ["<rootDir>/jest"],
  testMatch: ["**/*.test.ts", "**/*.test.tsx"],
  
  transform: {
    "^.+\\.tsx?$": ["ts-jest", {
      tsconfig: {
        jsx: "react-jsx"
      }
    }],
  },
  
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "\\.(css|less|scss|sass)$": "<rootDir>/jest/style-mock.ts",
  },
  
  setupFilesAfterEnv: ["<rootDir>/jest/setup-tests.ts"],

  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/main.tsx",
  ],
  
  verbose: true,
};

export default config;