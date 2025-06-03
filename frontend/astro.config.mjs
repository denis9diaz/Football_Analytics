// @ts-check
import { defineConfig } from 'astro/config';
import dotenv from 'dotenv';

import tailwindcss from '@tailwindcss/vite';

import react from '@astrojs/react';

dotenv.config();

// https://astro.build/config
export default defineConfig({
  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [react()]
});