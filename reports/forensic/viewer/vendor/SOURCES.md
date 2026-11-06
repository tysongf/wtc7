# Vendored browser libraries

Copied unchanged from the npm registry tarballs below, so the viewer needs no build step and no network.
`SHA256SUMS` covers the copied files; the tarball SHA-1 values are the registry's published `dist.shasum`,
checked on download (2026-11-05).

| File | From | Tarball | Tarball SHA-1 |
|---|---|---|---|
| `vue-3.5.13.global.prod.js` | `package/dist/vue.global.prod.js` | https://registry.npmjs.org/vue/-/vue-3.5.13.tgz | `9f760a1a982b09c0c04a867903fc339c9f29ec0a` |
| `three-0.147.0.min.js` | `package/build/three.min.js` | https://registry.npmjs.org/three/-/three-0.147.0.tgz | `1974af9e8e0c1efb3a8561334d57c0b6c29a7951` |
| `OrbitControls-0.147.0.js` | `package/examples/js/controls/OrbitControls.js` | same | same |

Three.js 0.147.0 is the last release with both the global (non-module) build and `examples/js/`. Browsers refuse
ES modules from `file://`, so a later Three.js would need a local server or a bundler. Licences: `LICENSE.vue`,
`LICENSE.three` (both MIT).
