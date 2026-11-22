# libmisb SDK

Use the standalone SDK to decode, encode, stream, and validate MISB ST 0601 metadata. The native SDK includes bindings and examples for C, C++, C#, Go, Java, and Python. The WebAssembly decoder runs in browsers and Node.js.

[Download the SDK](https://impleotv.github.io/libmisb-release/) · [Customer manual](https://impleotv.github.io/libmisb-release/manual/) · [All releases](https://github.com/impleotv/libmisb-release/releases)

Choose Windows x64, Linux x64, or macOS arm64. Each installer includes the native SDK and an optional web component. Portable native ZIPs, a static web ZIP, and an npm tarball are available separately.

Start in demo mode with the supplied `example.klv`. The [native quickstart](https://impleotv.github.io/libmisb-release/manual/docs/getting-started/) and [web quickstart](https://impleotv.github.io/libmisb-release/manual/docs/wasm-decoders/) show the commands and expected output.

Each release includes SHA-256 checksums and a versioned copy of the customer manual. To read the manual offline, extract its ZIP into an empty directory, run `python -m http.server 8000 --bind 127.0.0.1` in that directory, and open `http://127.0.0.1:8000/libmisb-release/manual/`.
