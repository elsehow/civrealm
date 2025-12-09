# CivRealm World Reports

A fork of [CivRealm](https://github.com/bigai-ai/civrealm) that adds comprehensive world report generation capabilities for analyzing Civilization games.

## About This Fork

This project builds on the excellent [CivRealm](https://github.com/bigai-ai/civrealm) framework developed by BIGAI, which provides a Gymnasium-compatible environment for the open-source strategy game [Freeciv-web](https://github.com/freeciv/freeciv-web).

**What's New:** We've extended CivRealm with a world report generation system that automatically produces detailed analytical reports from AI-vs-AI gameplay, including:
- Economic metrics and trade analysis
- Demographic trends and population statistics
- Technology advancement tracking
- Historical event timelines
- Interactive visualizations and territory maps

![Punic War](docs/assets/punic_war_base.jpg)

# Contents

- [About This Fork](#about-this-fork)
- [How It Works](#how-it-works)
  - [Running AI Games with run_world.py](#running-ai-games-with-run_worldpy)
  - [Data Production Pipeline](#data-production-pipeline)
  - [World Report Generation](#world-report-generation)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Testing the Installation](#testing-the-installation)
  - [Single player mode (against built-in AIs)](#single-player-mode-against-built-in-ais)
  - [Multiplayer mode](#multiplayer-mode)
- [Trouble Shooting](#trouble-shooting)
- [Original CivRealm Project](#original-civrealm-project)

## About

CivRealm is developed based on [freeciv-bot](https://github.com/chris1869/freeciv-bot), dependent on [freeciv-web](<https://github.com/freeciv/freeciv-web>) and [FCIV-NET](<https://github.com/fciv-net/fciv-net>).
In the future, CivRealm will be maintained by BIGAI.

## Prerequisites

CivRealm requires Python `≥ 3.8` and docker. We have tested on Ubuntu 22.04, Mac OS X, and Windows. 

To test CivRealm on <http://localhost>, please follow the docker installation instructions on <https://bigai-ai.github.io/civrealm/getting_started/requirements.html>.

After starting the Freeciv-web service, you can connect to the Freeciv-web server via the host machine <a href="http://localhost:8080/">localhost:8080</a> using a standard browser.

## Installation

Install with:

```bash
git clone git@github.com:bigai-ai/civrealm.git && cd civrealm
pip install -e .
```

<!-- 
### Update the freeciv-web image

Start the freeciv-web docker:

```bash
cd freeciv-web
docker compose up -d
```

Activate the civrealm virtual environment, and update the freeciv-web image:

```bash
update_freeciv_web_docker
```

Restart the freeciv-web container so that the change takes effect

```bash
cd freeciv-web
docker compose down
docker compose up -d
```
-->

## Testing the Installation

Before testing the installation, please make sure that the freeciv-web service is running. You can check the status of the freeciv-web service by running:

```bash
docker ps
```

You should see a docker container named `freeciv-web` running.

### Single player mode (against built-in AIs)

To test the installation, run the following command after installation. This will start a single player game against the built-in AIs with the default settings.

```bash
test_civrealm
```

!!! success
    If the installation is successful, the output should be similar to the following:

    ```bash
    Reset with port: 6300
    Step: 0, Turn: 1, Reward: 0, Terminated: False, Truncated: False, action: ('unit', 104, 'move NorthEast')
    Step: 1, Turn: 1, Reward: 0, Terminated: False, Truncated: False, action: ('unit', 117, 'move North')
    Step: 2, Turn: 1, Reward: 0, Terminated: False, Truncated: False, action: ('unit', 118, 'move North')
    Step: 3, Turn: 1, Reward: 0, Terminated: False, Truncated: False, action: ('unit', 119, 'move SouthEast')
    Step: 4, Turn: 1, Reward: 0, Terminated: False, Truncated: False, action: ('unit', 120, 'move SouthEast')
    ```

### Multiplayer mode

To test with multiple players, run the following command in a terminal to start the game with player `myagent`:

```bash
test_civrealm --minp=2 --username=myagent --client_port=6001
```

Then start another terminal and join the game with player `myagent1`:

```bash
test_civrealm --username=myagent1 --client_port=6001
```

<!-- ### Using a different freeciv version

As a standard, the official docker image from the [official repository](https://github.com/freeciv/freeciv-web) will be pulled. If you want to create a custom freeciv server (e.g., different rulesets, customizations, etc.) you can use `build_freeciv_server` to create a custom docker image or run a separate image in parallel. In this case, you might need to adapt src/init_server.py -->

## Trouble Shooting

The following are some common issues that you may encounter when running the code. If you encounter any other issues, please feel free to open an issue.

- If firefox keeps loading the page, please try to add the following line to `/etc/hosts`:

    ```bash
    127.0.0.1 maxcdn.bootstrapcdn.com
    127.0.0.1 cdn.webglstats.com
    ```

- If you see the following error when running `test_civrealm`,  please see [this solution](https://stackoverflow.com/questions/72405117/selenium-geckodriver-profile-missing-your-firefox-profile-cannot-be-loaded). If this does not solve the problem, please check `geckodriver.log` for more information.

    ```bash
    selenium.common.exceptions.WebDriverException: Message: Process unexpectedly closed with status 1
    ```

    One potential solution on Ubuntu 22.04 is:

    ```bash
    sudo apt install firefox-geckodriver
    ln -s /snap/bin/firefox.geckodriver geckodriver
    ```

- If you see the following error when setting `take_screenshot: True`, it is caused by snap version of Firefox. Please try [System Firefox installation](https://support.mozilla.org/en-US/kb/install-firefox-linux#w_install-firefox-from-mozilla-builds-for-advanced-users).

  ```bash
  Your Firefox profile cannot be loaded. 
  It may be missing or inaccessible.
  ```

- If the screenshot is not centered on the location of your first unit, it is because you are using multiple displays. Please ensure the Firefox browser for screenshot pops up on your primary display.

## Check out our paper

Our paper is available on [Arxiv](https://arxiv.org/abs/2401.10568). If you find our code or databases useful, please consider citing us:

```bibtex
@inproceedings{qi2024civrealm,
  title     = {CivRealm: A Learning and Reasoning Odyssey in Civilization for Decision-Making Agents},
  author    = {Siyuan Qi and Shuo Chen and Yexin Li and Xiangyu Kong and Junqi Wang and Bangcheng Yang and Pring Wong and Yifan Zhong and Xiaoyuan Zhang and Zhaowei Zhang and Nian Liu and Wei Wang and Yaodong Yang and Song-Chun Zhu},
  booktitle = {International Conference on Learning Representations},
  year      = {2024},
  url       = {https://openreview.net/forum?id=UBVNwD3hPN}
}
```
