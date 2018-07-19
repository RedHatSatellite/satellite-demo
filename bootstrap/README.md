# Usage bootstrap image

This image is designed to be fully able to run the playbooks for this demo.

Check out [what's needed to build the image.](NEEDED.md)

It uses the following environment varibles:

- `AWS_ACCESS_KEY` for your access key into AWS
- `AWS_SECRET_KEY` for the secret key to the access key
- `SUBSCRIPTION_ORG` satellite org used to register the satellite server

Together, they allow the playbooks to create and manage AWS resources for the demo.

If you copy the `aws.sample` file to `aws`, then the `Makefile` will automatically ensure that the container when ran has those environments set.

```bash
cd bootstrap
cp aws.sample aws
vi aws
# edit the KEYS and save
```

To run the bootstrap:

```bash
cd bootstrap
make
# so you can disconnect and come back later
screen -S bootstrap
make run
```
# Usage playbooks

After you're in the bootstrap container, you should just need to run make. It
has the proper order defined, and will prevent you from running playbooks that
already finished properly.

```bash
make all
```

And when you're done:

```bash
make clean
```
