# Contributing

Feel free to actively contribute to this project by opening pull requests. They
will all be considered.


### Development workflow

There are two main branches: `main`, which is the base branch, and
`develop`, which is the branch where new features are merged. All
created pull requests should be merged into the `develop` branch. From
time to time, the content of the `develop` branch is merged into the
`main` branch, where new releases are created.

The Nebulapicker application is divided into two components: the backend API
application and the frontend web application. The first is located in the
`app/api` directory, while the second is in the `app/web`
directory. Development of each application should be done separately.


### API Development

The API is developed using FastAPI. All development commands can be executed
with Make. To run these commands, you must first navigate to the `app/api`
directory.

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

There is a GitHub workflow that validates tests, coverage, and linting before
merging pull requests.


### Web Development

The web application is developed using Next.js. Development commands rely on
npm. To run these commands, you must first navigate to the `app/web` directory.

Install the required packages:
```bash
npm install
```
Then, you can deploy using the dev mode:
```bash
npm run dev
```

Currently, the build process of the web application includes a linter, which is
also part of the Web CI GitHub workflow. The local command to check linting is:
```bash
npm run lint
```
The local command to apply lint changes is:
```bash
npm run lint:fix
```

To build the web application:
```bash
npm run build
```
The build can also be performed when generating the Docker image:
```bash
docker build --build-arg API_DESTINATION=http://api:8000 -t nebulapicker-web -f Dockerfile .
```

There is a GitHub workflow that validates the build and linting before merging
pull requests.


### Creating new releases

The first step in creating a new release is to build and push the Docker images
(API and Web) for NebulaPicker. Releases can only be created from the `main`
branch, so make sure that `main` is rebased with develop before proceeding.
Next, create a new tag following [Semantic Versioning](http://semver.org/),
e.g., v0.1.1. Both images must have the same version tag. A workflow will be
triggered automatically when a new tag is pushed to the `main` branch. Before
merging code into `main` and creating the version tag, don’t forget to update
the version number in the following files:
- `README.md`
- `app/api/main.py`
- `app/web/package-lock.json`
- `app/web/package.json`

Thus, the steps to create a new release are as follows:
1. Build and push the new Docker images for NebulaPicker-api and
nebulapicker-web.
2. Create a pull request that updates the version tag in the files
mentioned above, and merge it into the develop branch.
3. Rebase the `main` branch.
4. Create a new tag with the updated version in the `main` branch.
