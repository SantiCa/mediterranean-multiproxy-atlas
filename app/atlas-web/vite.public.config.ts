import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

export default defineConfig({
  root: fileURLToPath(new URL("./public-viewer", import.meta.url)),
  publicDir: false,
  appType: "mpa",
  plugins: [react()],
  define: { __ATLAS_PUBLIC_VIEWER__: "true" },
  build: {
    outDir: fileURLToPath(new URL("./dist-public", import.meta.url)),
    emptyOutDir: true,
    sourcemap: false,
  },
});
