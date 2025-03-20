import { defineConfig } from '@rslib/core';
import { version } from "./package.json";

export default defineConfig({
  lib: [
    {
      format: 'cjs',
      syntax: 'es2021',
    },
  ],
  source: {
    define: {
      'process.env.PACKAGE_VERSION': JSON.stringify(version),
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }
  },
});
