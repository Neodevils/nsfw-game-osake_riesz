# Osake Riesz Ruffle Wrapper

Browser wrapper for `osake_riesz_e.swf` using Ruffle.

## Notice

I do not own Osake Riesz or its original game assets. This repository only hosts a browser-playable copy for the Discord community in case people want to play it through a modern browser/Ruffle setup.

If you are a rights holder and want this removed or changed, please contact the repository owner.

## Play Online

https://neodevils.github.io/osake_riesz_ver1.13/

## Run Locally

```sh
python3 -m http.server 8080
```

Then open http://localhost:8080.

The `data/` directory must stay beside `osake_riesz_e.swf`; the main SWF loads its supporting SWFs from that relative path.
