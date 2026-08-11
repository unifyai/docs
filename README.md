# Unify Documentation

## Setup

### Build the docker image

```
docker build -t docs:latest -f Dockerfile .
```

### Run the docker image

```
docker run -v .:/docs -p 3000:3000 docs:latest
```

The docs should be live at localhost:3000.

### Restart the container

The `mintlify dev` command downloads the mintlify framework everytime we create a new container which takes some time to complete.

In order to save time, I'd suggest just restarting the previously existing container rather than creating a new one, the docker image only really contains the `node:bookworm` docker image and the installation of `mintlify`.

```
docker restart <container-id>
```

Of course, you can spin up a new container every once in a while if either of the 2 get updated.

## Brand assets

The theme (`docs.json`) follows the Unify shared light system: paper/ink canvas, teal `#2f9d97` primary, Space Grotesk headings, and Inter body.

The banner and OG image in `images/` (`unify-docs-banner-*.svg`, `unify-docs-og.png`) are rendered from the `branding` repo — do not hand-edit them. To regenerate, run `npm run render:docs-diagrams` in `branding/` and copy the refreshed files from `branding/assets/docs/` into `images/`.
