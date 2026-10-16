import { defineConfig, mergeConfig } from 'vite';
import { fileURLToPath } from 'node:url';
import base from './vite.config.ts';
// Set before Vite loads any .env files; this takes precedence over file values.
process.env.VITE_API_BASE = '/api';
export default mergeConfig(base, defineConfig({define:{'import.meta.env.VITE_API_BASE':JSON.stringify('/api')},build:{
  outDir:'local-demo-dist',
  rollupOptions:{input:{app:fileURLToPath(new URL('./index.html',import.meta.url)),
    bridge:fileURLToPath(new URL('./samples/bridge.html',import.meta.url))}},
}}));
