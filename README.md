# Osake Riesz Ruffle Wrapper

Private browser wrapper for `osake_riesz_e.swf` using Ruffle.

## Run Locally

```sh
python3 -m http.server 8080
```

Then open http://localhost:8080.

The `data/` directory must stay beside `osake_riesz_e.swf`; the main SWF loads its supporting SWFs from that relative path.
