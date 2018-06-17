# open-taxi

## Development

To make a local Python virtual env and install dependencies specified in requirements.txt:

```
$ make activate
$ make install
```

Then run `make test`

## Configuration

Custom parameters defined in your [CloudFormation template](./template.yaml) can have overrides specified in [template_params.txt](./template_params.txt).

# Deployment

Before deployment your Lambda code is uploaded to your deployment bucket using the AWS
CLI package command.

```
$ make clean    # if previously built
$ make build    # after code changes
$ make package  # after code or CloudFormation changes
$ make deploy
```
