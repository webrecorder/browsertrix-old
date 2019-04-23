# Browsertrix

[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![Build Status](https://travis-ci.org/webrecorder/browsertrix.svg?branch=master)](https://travis-ci.org/webrecorder/browsertrix)

## High Fidelity Browser-Based Crawling Automation

Browsertrix is a brand new system from the Webrecorder project for automating browsers to perform complex scripted behaviors
as well as crawl multiple pages. (The name was originally used for an older project with similar goals).

Browsertrix uses Docker to manage the operation of multiple Chrome based browsers, operated via the CDP protocol, and uses [pywb](https://github.com/webrecorder/pywb) proxy mode for capture and replay.

It includes the following features:
* Crawling with different basic scope rules (Single Page, All Links, Same Domain, and custom)
* Execution of complex domain specific in-page behaviors (provided by [webrecorder/behaviors](https://github.com/webrecorder/behaviors))
* Capture or replay into designated pywb collections
* Optional screenshot creation of each page.
* Support for customized browser profiles to minimize capture of private information.

## Getting Started

### Installing Browsertrix

Browsertrix is currently designed to run with Docker and Docker Compose.
The Browsertrix CLI requires local Python 3.6+

To install, run:

```bash
git clone https://github.com/webrecorder/browsertrix
cd browsertrix
python setup.py install
./install-browsers.sh
docker-compose build
docker-compuse up -d
```

The `install-browsers.sh` script installs additional containers necessary for dynamic browser creation.
The script can be used to update the containers as well.

### Installing Browsertrix CLI

The Browsertrix CLI is installed by running `python setup.py install` and includes full functionality for running crawls and creating browser profiles.

Once installed, browsertrix commands are available via the `browsertrix` command.

## Creating a Crawl

To create a crawl, first a crawl spec should be defined in a yaml file.
A simple spec, ``example_spec.yaml`` might look as follows:

```yaml
crawls:
  - name: test-crawl
    crawl_type: single-page
    num_browsers: 1

    coll: example
    mode: record

    seed_urls:
      - http://example.com/
```

Then, simply run `browsertrix crawl create example_spec.yaml --watch`

The `--watch` param will also result in the crawling browser opening in a new browser window via VNC.

The spec may have multiple crawls defined and all be started.

### Crawling Options

Browsertrix supports a number of options, with a key option being the `crawl_type`, which can be:

- `single-page = crawl only the specified page
- `all-links` = crawl all links on this page
- `same-domain` = crawl all links within this domain (upto a depth of 100)
- `custom` = Supports custom depth and scope rules!

When using `custom`, the `crawl_depth` param can specify the crawl depth (hops) from each seed url.
The `scopes` list can contain one or more [urlcanon MatchRules](https://github.com/iipc/urlcanon/blob/master/python/urlcanon/rules.py#L70) specifying urls that are in scope for the crawl.


The `coll` option specifies the pywb collection to use for crawling, and mode specifies `record` (default) or `replay` or
`live` (direct live web connection).

The `num_browsers` and `num_tabs` option allow for selecting total number of browsers and number of tabs per browser to use for this crawl.

### pywb Collections and Access

All data crawled is placed in the `./webarchive/collections/` directory which corresponds to the [standard pywb directory structure conventions](https://pywb.readthedocs.io/en/latest/manual/configuring.html#directory-structure) eg. a collection `test` would be found under `./webarchive/collections/test`.

Collections are created automatically on first use and can also be managed via `wb-manager` with `webarchive` as the working directory.

The running pywb instance can also be accessed via `http://localhost:8180/`

### Replay Crawling and Screenshots

Browsertrix supports crawling in replay mode, over an existing collection, which may be useful for QA processes,
especially when combined with screenshot creation.

By adding the `screenshot_coll` property to each crawl, Browsertrix will also create a screenshot of each page.
Additional screenshot options are to be added soon! (Currently, the screenshot is taken after the behavior is run).

Crawl options can also be overriden via command line.

For example, given a crawl spec `./my_crawl.yaml`, one could first capture with:
```
browsertrix crawl create ./my_crawl.yaml --screenshot_coll screenshots-capture
```

and then run:
```
browsertrix crawl create ./my_crawl.yaml --screenshot_coll --mode replay screenshots-qa
```

By default, screenshots are saved with `urn:screenshot:<url>` prefix.
Based on the above crawls, one could then query all capture and qa screenshots in pywb via:
```
http://localhost:8180/screenshots-capture/*/urn:screenshot:*
http://localhost:8180/screenshots-qa/*/urn:screenshot:*
```

(The screenshot functionality will likely change and additional options will be added)

### Other Crawl operations

Browsertrix also includes other operations, such as `browsertrix list` for listing crawls,
and `browsertrix watch <crawl_id>` for attaching and watching all the browsers in a given crawl.

See `browsertrix crawl -h` for a complete reference of availablecommands


## Browser Profiles

It is often useful to prepare a browser, such as by logging into social media, other password protected sites
to be able to capture content that is not generally accessible. However, doing so during a crawl is tedious, and worse,
may result in passwords being recorded to WARC.

Browsertrix addresses this problem with the support of browser profiles. A profile can be created by running a base
Chrome browser, performing custom actions, and then 'saving' the running browser into a new 'profile' image.

To create a profile:

1. Run:
```browsertrix profile create```

2. This should start a new remote browser (Chrome 73 by default) and open it in a new window. You can now interact with the browser and log in to any sites as needed.

3. The command line should have the following message and a prompt to enter the profile name, eg. `social-media`

```
A new browser window should have been opened
You can use the browser to log-in to accounts or otherwise prepare the browser profile
(The content will not be recorded to WARC)
When done, please enter a new name to save the browser profile: 
```

4. Once the name is entered the profile is saved, and you can continue browsing to make a new profile, or select 'no' and close the browser.

To use the profile, set the `profile: ` property in the crawl spec YAML, or add it to the command line:
```
browsertrix crawl create ./my_crawl.yaml --profile social-media
```

The browsers used for the crawl will be a copy of the browser saved during profile creation.

`browsertrix profile list` and `browsertrix profile remove` allow for profile listing and removal, respectively.

Note: The profile functionality is brand new and subject to change. At present, it is tied to the particular browser Docker image used an extend the image. The system may switch to Docker volumes in the future.

## Testing

Browsertrix includes several test suites, also tested on automatically via Travis CI.

### Docker Integration Tests

Browsertrix includes a Docker-based test suite that runs crawls over content replayed from a WARC
(no live web content is accessed). This test suite requires Python 3.6+.

To run this test suite, run:

```bash
bash ./tests/start-test-compose.sh
pip install -U -r test-docker-requirements.txt
py.test --headless ./tests/test_live_crawl.py
bash ./tests/stop-test-compose.sh
```

### Local API Tests

To install and run local tests of the API (without Docker), run the following:
(Python 3.7+ is required)

```bash
pip install -U -r requirements.txt -r test-local-requirements.txt
py.test ./tests/test_api.py
```

## Frontend

Browsertrix also includes a frontend (still under development) which will
have the same features as the CLI.

To access the browsertrix frontend, load `http://localhost:8000/`

The frontend React app is found in `./frontend` and can be started via:

```
yarn run develop
```

(The develop server is started at `http://localhost:8001` to avoid conflict with production)

To build the production bundle, run:
```
yarn run build-prod
```

This should update the production server running at `http://localhost:8000`
