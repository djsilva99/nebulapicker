# nebulapicker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/djsilva99/nebulapicker/blob/main/LICENSE)
[![API API](https://github.com/djsilva99/nebulapicker/actions/workflows/test_api.yaml/badge.svg?branch=main)](https://github.com/djsilva99/nebulapicker/actions/workflows/test_api.yaml)
[![API WEB](https://github.com/djsilva99/nebulapicker/actions/workflows/test_web.yaml/badge.svg?branch=main)](https://github.com/djsilva99/nebulapicker/actions/workflows/test_web.yaml)
[![codecov](https://codecov.io/github/djsilva99/nebulapicker/graph/badge.svg?token=Y5HGCKRYCK)](https://codecov.io/github/djsilva99/nebulapicker)

<p>
    <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/nebulapicker.png" alt="Drawing" height="30"/> nebulapicker v1.0.0
</p>

🚀 Stay informed without drowning in noise. NebulaPicker lets you shape your
own RSS feeds by filtering and refining content from the sources you trust.

NebulaPicker is a self-hosted web application for content curation, designed to
streamline and automate the process of filtering online information. It acts as
a personalized feed generator that helps users stay focused on relevant content
while reducing noise from high-volume information sources.

The application works by aggregating articles and updates from multiple RSS
feeds, processing them according to user-defined rules, and producing a clean,
curated output tailored to individual interests or workflows.

**Core Features**

- Fetches content automatically from multiple RSS sources using scheduled CRON
  jobs.
- Applies customizable filters to remove unwanted content.
- Publishes a refined, distraction-free feed adapted to specific interests.
- Runs entirely self-hosted, giving users full control over their data and
  infrastructure.

**How It Works**

NebulaPicker periodically retrieves entries from configured RSS feeds. Each
item is then evaluated against filtering rules defined by the user. These rules
can include keyword matching, or exclusion filters. After processing, only
relevant entries are included in the final curated feed, which can be consumed
through standard RSS readers or integrated into other workflows.

**Available Editions**

Currently, NebulaPicker is available in two flavors:
- _Original Edition_: focuses exclusively on managing and filtering RSS feed
items. This lightweight version is ideal for users who want simple aggregation
and filtering without additional processing.
- _Content Extractor Edition_: integrates with Wallabag to extract and store
full article content, enabling a richer reading and knowledge-management
experience.

## Example
Original Edition:

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/original.gif" alt="Original Edition" style="width: 100%; height: auto;"/>

<p align="center">
  <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/original_mobile.gif"
       alt="Original Edition for mobile"
       style="width: 80%; height: auto;" />
</p>

Content Extractor Edition:

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/content_extractor.gif" alt="Original Edition" style="width: 100%; height: auto;"/>

<p align="center">
  <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/content_extractor_mobile.gif"
       alt="Original Edition for mobile"
       style="width: 80%; height: auto;" />
</p>


## Run the Original Edition using docker compose
To run the API without setting up a local environment, start the full
application (API + database + WEB) using Docker Compose:
```bash
docker-compose up -d
```

Currently, NebulaPicker comes with basic authentication. The default username
and password are both `nebulapicker`. To change them, update the corresponding
variables in the `.env` file.

To stop the Original Edition with docker compose:
```bash
docker-compose down
```

## Run the Content Extractor Edition using docker compose
The Content Extractor Edition can be started as well using Docker Compose
(Wallabag + API + database + WEB):
```bash
docker-compose -f docker-compose-with-extractor.yaml up -d
```

To use Wallabag as a content extractor, you first need to create a Wallabag API
client. After launching the application with Docker Compose, log in to the
[Wallabag frontend](http://localhost:8081) using the username `wallabag` and
password `wallabag`. In "My Account", select "API Clients Management". Create a
new client and copy the generated Client ID and Client Secret. Paste these
values into the environment variables `WALLABAG_CLIENT_ID` and
`WALLABAG_CLIENT_SECRET` in the `.env.with_extractor` file.

Finally, relaunch the application:
```bash
docker-compose -f docker-compose-with-extractor.yaml up -d
```

The default username and password are again both `nebulapicker`. To change
them, update the corresponding variables in the `.env.with_extractor` file.

To stop the Content Extractor Edition with docker compose:
```bash
docker-compose -f docker-compose-with-extractor.yaml down
```


## Contributing

Feel free to actively contribute to this project by opening pull requests. They
will all be considered. To make it easier, please visit the [contributing
documentation](https://github.com/djsilva99/nebulapicker/blob/main/CONTRIBUTING.md).
