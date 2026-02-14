# nebulapicker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/djsilva99/nebulapicker/blob/main/LICENSE)
[![API API](https://github.com/djsilva99/nebulapicker/actions/workflows/test_api.yaml/badge.svg?branch=main)](https://github.com/djsilva99/nebulapicker/actions/workflows/test_api.yaml)
[![API WEB](https://github.com/djsilva99/nebulapicker/actions/workflows/test_web.yaml/badge.svg?branch=main)](https://github.com/djsilva99/nebulapicker/actions/workflows/test_web.yaml)
[![codecov](https://codecov.io/github/djsilva99/nebulapicker/graph/badge.svg?token=Y5HGCKRYCK)](https://codecov.io/github/djsilva99/nebulapicker)

<p>
    <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/nebulapicker.png" alt="Drawing" height="30"/> nebulapicker v1.0.0
</p>

🚀 Stay informed without drowning in noise.

NebulaPicker is a self-hosted RSS feed generator that filters and refines
content from multiple trusted sources to produce clean, personalized feeds
tailored to your interests.

It aggregates entries from external RSS feeds, applies user-defined filtering
rules, and publishes a curated output that can be consumed by any RSS reader or
integrated into automated workflows.

✨ **Core Features**
- Automatically fetches content from multiple RSS sources using CRON jobs
- Custom filtering rules to remove unwanted noise
- Generates clean, focused RSS feeds
- Fully self-hosted — complete control over data and infrastructure

📦 **Available Editions**

_Original Edition_ — lightweight RSS generator aggregating and filtering
external sources

_Content Extractor Edition_ — integrates with Wallabag to archive and read full
articles.


## 🎬 Example

**Original Edition:**

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/original.gif" alt="Original Edition" style="width: 100%; height: auto;"/>

<p align="center">
  <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/original_mobile.gif"
       alt="Original Edition for mobile"
       style="width: 80%; height: auto;" />
</p>

**Content Extractor Edition:**

<img src="https://github.com/djsilva99/nebulapicker/blob/main/img/content_extractor.gif" alt="Original Edition" style="width: 100%; height: auto;"/>

<p align="center">
  <img src="https://github.com/djsilva99/nebulapicker/blob/main/img/content_extractor_mobile.gif"
       alt="Original Edition for mobile"
       style="width: 80%; height: auto;" />
</p>


## 🚀 Quick Start (Docker Compose)

NebulaPicker can be started instantly using Docker Compose — no local setup
required.

### Original Edition
Runs the API, database, and web interface:
```bash
docker-compose up -d
```

Default credentials:
- username: `nebulapicker`
- password: `nebulapicker`

You can change them in the `.env` file.

Stop the application:
```bash
docker-compose down
```

### Content Extractor Edition
Includes Wallabag integration for full article extraction.

Start the stack:
```bash
docker-compose -f docker-compose-with-extractor.yaml up -d
```

Configure Wallabag:
1. Open http://localhost:8081
2. Login with:
   - username: wallabag
   - password: wallabag
3. Go to My Account → API Clients Management
4. Create a client and copy:
   - Client ID
   - Client Secret
5. Add them to .env.with_extractor:
   - `WALLABAG_CLIENT_ID=`
   - `WALLABAG_CLIENT_SECRET=`

Restart the stack:
```bash
docker-compose -f docker-compose-with-extractor.yaml up -d
```

Default NebulaPicker credentials remain:
- username: `nebulapicker`
- password: `nebulapicker`

Finally, to stop the stack:
```bash
docker-compose -f docker-compose-with-extractor.yaml down
```


## 🤝 Contributing

Contributions are welcome!  Feel free to open issues or pull requests — see the
[contributing
guide](https://github.com/djsilva99/nebulapicker/blob/main/CONTRIBUTING.md) for
details.
