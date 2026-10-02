# docker-env-test

A minimal container that serves a web page listing the process environment variables. **For testing and debugging only** — do not deploy this where untrusted users can reach it. The page exposes every variable in the container, including secrets passed via `-e` or env files.

## Build

```bash
docker build -t docker-env-test .
```

## Run

Map host port **8080** to the container (the app listens on 8080 inside the image):

```bash
docker run --rm -p 8080:8080 docker-env-test
```

Open [http://localhost:8080/](http://localhost:8080/) in a browser.

### Example with custom variables

```bash
docker run --rm -p 8080:8080 \
  -e MY_VAR=example \
  -e ANOTHER=value \
  docker-env-test
```

### Map a different host port

```bash
docker run --rm -p 9090:8080 docker-env-test
```

Then visit [http://localhost:9090/](http://localhost:9090/).

## What it does

- `EXPOSE 8080` in the image
- `server.py` responds to `GET /` with an HTML table of sorted environment variable names and values
