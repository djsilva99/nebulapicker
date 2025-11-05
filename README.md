# nebulapicker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/djsilva99/nebulapicker/blob/main/LICENSE)
[![API API](https://github.com/djsilva99/nebulapicker/actions/workflows/test_api.yaml/badge.svg?branch=main)](https://github.com/djsilva99/nebulapicker/actions/workflows/test_api.yaml)
[![API WEB](https://github.com/djsilva99/nebulapicker/actions/workflows/test_web.yaml/badge.svg?branch=main)](https://github.com/djsilva99/nebulapicker/actions/workflows/test_web.yaml)
[![codecov](https://codecov.io/github/djsilva99/nebulapicker/graph/badge.svg?token=Y5HGCKRYCK)](https://codecov.io/github/djsilva99/nebulapicker)

<p>
    <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/nebulapicker.png" alt="Drawing" height="30"/> nebulapicker v0.3.0
</p>

NebulaPicker is a self-hosted Web Application for content curation, designed to
streamline and automate the process of filtering online information. It acts as
a personalized feed generator that:
- fetches content from multiple RSS sources using CRON jobs.
- applies user-defined filters to remove noise.
- publishes a clean feed tailored to specific interests.


## Example
Feed settings:

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/feed_settings.png" alt="Feed Settings"  style="width: 100%; height: auto;"/>

Feed content:

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/feed_content.png" alt="Feed Content"  style="width: 100%; height: auto;"/>

Generated rss:

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/feed_rss.png" alt="Feed RSS"  style="width: 100%; height: auto;"/>


## Run the full application using docker compose
To run the API without setting up a local environment, start the full
application (API + database + WEB) using Docker Compose:
```bash
docker-compose -f docker-compose-full.yaml up -d
```

To stop the full application with docker compose:
```bash
docker-compose -f docker-compose-full.yaml down
```


## Contributing

Feel free to actively contribute to this project by opening pull requests. They
will all be considered.To make it easier, please visit the [contributing documentation](https://github.com/djsilva99/nebulapicker/blob/main/CONTRIBUTING.md)
They will all be considered.
