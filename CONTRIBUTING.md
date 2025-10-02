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

Creating a new nebulapicker release is only possible from the `main`
branch. To do so, one needs to create a new tag, relying on 
[Semantic Versioning](http://semver.org/), e.g., v0.1.1. There is a
workflow that is triggered by pushing new tags into the `main` branch.
Do not forget to change the new version tag in the documentation before
merging code into the `main` branch and creating the version tag:
- README.md

Thus, the steps that create a new release are the following:

1. Create a PR that adds the new version tag into the locations
   pointed out above. Merge it into the develop branch.
2. Merge into the develop branch into the `main` branch.
3. Create a tag with the new version in the `main` branch.
