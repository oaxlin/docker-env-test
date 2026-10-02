# docker-env-test

A minimal container that serves a web page listing the process environment variables. **For testing and debugging only** — do not deploy this where untrusted users can reach it. The page exposes every variable in the container, including secrets passed via `-e` or env files.

## Build

```bash
docker build -t docker-env-test .
```

## Run

Map host port **443** to the container (the app listens on 443 inside the image):

```bash
docker run --rm -p 443:443 docker-env-test
```

Open [http://localhost/](http://localhost/) in a browser. Traffic is plain HTTP on port 443 (no TLS).

### Example with custom variables

```bash
docker run --rm -p 443:443 \
  -e MY_VAR=example \
  -e ANOTHER=value \
  docker-env-test
```

### Map a different host port

```bash
docker run --rm -p 8443:443 docker-env-test
```

Then visit [http://localhost:8443/](http://localhost:8443/).

## What it does

- `EXPOSE 443` in the image
- `server.py` responds to `GET /` with an HTML table of sorted environment variable names and values
