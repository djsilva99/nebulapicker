# Contributing

Feel free to actively contribute to this project by opening pull
requests. They will all be considered.


### Development workflow

There are two main branches: `main`, which is the base branch, and
`develop`, which is the branch where new features are merged. All
created pull requests should be merged into the `develop` branch. From
time to time, the content of the `develop` branch is merged into the
`main` branch, where new releases are created.

All executions can be done using make.

To deploy nebulapicker locally:
```bash
$ make install
$ make docker-compose-dev
$ make local-deployment
```

To stop deploying locally, do not forget to stop docker:
```bash
$ make docker-compose-dev-down
```

Tests rely on pytest, with coverage (must exceed 85%), and can be
executed with:
```bash
(env) $ make test
```

Lint should also pass:
```bash
(env) $ make lint
```
If not, you can re-format automatically:
```bash
(env) $ make apply-lint
```

There is a workflow that validates the tests, coverage and lint before
merging pull requests. They must all pass.


### Creating new releases

The first step in creating a new release is to build and push the
Docker image for NebulaPicker. Releases can only be created from the
`main` branch, so make sure that `main` is rebased with develop
before proceeding. Next, create a new tag following
[Semantic Versioning](http://semver.org/), e.g., v0.1.1. A workflow
will be triggered automatically when a new tag is pushed to the
`main` branch. Before merging code into `main` and creating the
version tag, don’t forget to update the version number in the
following files:
- `README.md`
- `main.py`

Thus, the steps to create a new release are as follows:
1. Build and push a new Docker image for NebulaPicker.
2. Create a pull request that updates the version tag in the files
mentioned above, and merge it into the develop branch.
3. Rebase the `main` branch.
4. Create a new tag with the updated version in the `main` branch.
