# These are the needed packages to build this image:

* podman
* buildah
* screen (so you can leave it and come back)
* git
* make

# for Fedora based distros:

You should just need to run this:

```bash
sudo yum install -y podman buildah screen git make
```

Then run:

```bash
make
make run
```

Make sure to read the [README.md](./README.md) file.
