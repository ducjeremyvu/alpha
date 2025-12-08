import tailwindcss from '@tailwindcss/vite';
import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit(), devtoolsJson()],
  server: {
    host: true,
    allowedHosts: ["homeassistant.fritz.box"]
  },
  proxy: {
    "/": {
      target: "http:homeassistant.fritz.box:8000",
      changeOrigin: true,
      rewrite: (p) => p.replace(/^\/api/, ""),

    }
  }
});


