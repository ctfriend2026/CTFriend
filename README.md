<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">CTFriend</h3>

  <p align="center">
    Agentic AI framework that leverages MCP servers to aid CTF participants.
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#grafana-setup">Grafana Setup</a>
      <ul>
        <li><a href="#prometheus-setup">Prometheus Setup</a>
        <li><a href="#postgresql-setup">PostgreSQL Seetup</a>
        <li><a href="#setup-dashboards">Setup Dashboards</a>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

[![CTFriend Screen Shot][product-screenshot]](http://128.239.26.203:8501/)

CTFriend is an agentic framework that leverages MCP servers to provide an
external chat-based server to aid CTF particpants. Additionally, CTFriend
provides logging to gain insights into human-AI interaction.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* Python
* FastMCP
* Docker
* Postgres
* Grafana

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Setting up CTFriend, setup has been wrapped into Docker containers controlled with Docker Compose. While, bare-metal installation is possible, for networking ease of use. Deployment should be done with Docker.

### Prerequisites

The only required prerequsite is Docker and Docker compose. For installation of Docker compose, follow this tutorial from Docker.

* <https://docs.docker.com/compose/install/>

### Installation

1. Clone the repo
    ```bash
    git clone git@github.com:TribeCTF/TribeCTF-AI.git
    ```

2. Setup environment variables
    ```bash
    cp .env.example .env

    # replace POSTGRES_PASSWORD, TOKEN_SECRET_KEY, and ANTHROPIC_API_KEY
    # NOTE: A personal ANTHROPIC KEY is needed for testing
    ```

3. Install Docker containers

    _Insure docker is running_

   ```sh
   docker-compose up --build
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Generating User Tokens

CTFriend works on whitelisting tokens, where each user has their own individual token to ID them and their chats within the system. To create this token, use the following instructions.

Login into the ctfriend container and run the following commands:

```bash
cd app

python3 token_manager.py whitelist [email]
```

## Grafana Setup

Configure Grafana:

Open your web browser and go to http://\<hosted-ip>:3000.

Log in with the:

* username: admin
* password: admin.

### Prometheus Setup

Add the Prometheus Data Source:

Go to "Connections" -> "Data Sources" -> "Add new data source".

![Add data source][data-source]

Select "Prometheus".

![Prometheus][prometheus-source]

For the "Prometheus server URL", enter `http://prometheus:9090`.

![Prometheus settings][prometheus-settings]

Click "Save & Test".

### PostgreSQL Setup

Add the PostgreSQL Data Source:

Go to "Connections" -> "Data Sources" -> "Add new data source".

Select "PostgreSQL".

![PostgreSQL Settings][postgres-source]

Use the following connection details:

* Name: postgres_db

* Host: db:5432

* Database: metrics

* User: \<username>

* Password: \<password>

* TLS/SSL Mode: disable

* Version: 15

* Timescale DB: True

![Postgres Settings1][postgres-settings1]
![Postgres Settings2][postgres-settings2]

Click "Save & Test". You might need to give Grafana's data source a specific UID like postgres_db if you want it to automatically link with the chat data dashboard.

### Setup Dashboards

Import the Dashboards:

Go to "Dashboards" -> "New" -> "Import".

![Dashboard Import][dashboard-import]

Upload the grafana-system-dashboard.json file. Select the "Prometheus" data source when prompted.

Repeat the process for the grafana-chat-dashboard.json file, selecting the "PostgreSQL" data source.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Backups
```bash
# view/manage cron jobs
crontab -l

# edit a cron job
crontab -e

# job for backing up CTFriend
*/5 * * * * "/home/ctfadmin/CTFriend/backup.sh" >> "/home/ctfadmin/CTFriend/crontab.out" 2>&1
```

<!-- ROADMAP -->
## Roadmap

* [x] UI Framework setup
* [x] API Key support
* [x] Multi-LLM Support
  * [x] Gemini
  * [x] OpenAI
  * [x] Ollama
* [x] MCP Support
  * [x] CyberChef
  * [x] RAG Knowledge Base


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: images/app_screenshot.jpg
[data-source]: images/data_source.jpg
[prometheus-source]: images/prometheus.jpg
[prometheus-settings]: images/prometheus-settings.jpg
[postgres-source]: images/postgres_source.jpg
[postgres-settings1]: images/postgres_settings1.jpg
[postgres-settings2]: images/postgres_settings2.jpg
[dashboard-import]: images/dashboard_import.jpg
