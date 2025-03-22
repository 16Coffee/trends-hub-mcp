import { defineConfig } from '@rslib/core';
import { version } from './package.json';
import { readmePlugin } from './scripts/readme';
import path from 'node:path';

export default defineConfig({
  lib: [
    {
      format: 'esm',
      syntax: 'es2021',
      dts: true,
    },
    {
      format: 'cjs',
      syntax: 'es2021',
    },
  ],
  source: {
    define: {
      'process.env.PACKAGE_VERSION': JSON.stringify(version),
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
    },
  },
  plugins: [readmePlugin({ readmePath: path.resolve('README.md') })],
});
