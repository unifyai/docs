# Unify Documentation

## Setup

### Build the docker image

```
docker build -t docs:latest -f Dockerfile .
```

### Run the docker image

```
docker run -v .:/unify-docs -p 3000:3000 docs:latest
```

The docs should be live at localhost:3000.

### Restart the container

The `mintlify dev` command downloads the mintlify framework everytime we create a new container which takes some time to complete.

In order to save time, I'd suggest just restarting the previously existing container rather than creating a new one, the docker image only really contains the `node:bookworm` docker image and the installation of `mintlify`.

```
docker restart <container-id>
```

Of course, you can spin up a new container every once in a while if either of the 2 get updated.
