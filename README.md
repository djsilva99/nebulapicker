# nebulapicker
NebulaPicker is a self-hosted API for content curation, designed to streamline
and automate the process of filtering online information. It acts as a
personalized feed generator that:
- fetches content from multiple RSS sources,
- applies user-defined filters to remove noise, and
- publishes a clean feed tailored to specific interests.


## Run the full application using docker compose
To run the API without setting up a local environment, start the full
application (API + database) using Docker Compose:
```
docker-compose -f docker-compose-full.yaml up -d
```
or use make:
```
make docker-compose-full
```

To stop the full application with docker compose:
```
docker-compose -f docker-compose-full.yaml down
```
or use make:
```
make docker-compose-full-down
```


## Run the application locally in dev mode
To run the API locally in dev mode:
```
make docker-compose-dev
```
to stop the postgres db:
```
make docker-compose-dev-down
```
