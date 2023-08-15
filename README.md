# newsfaces


## Usage

## Helpful Commands

`beaker show` to see the current state of the database.

## 1. Seeds

To work on a particular source, you'll need to start by running a seed
to get some initial data.

`beaker seeds` will list all the available seeds.

`beaker seed <seed_name>` will run the seed.

For test purposes, it is useful to run `beaker seed <seed_name> -rn 100`

* -r resets the seed first, useful for testing
* -n <number> will limit the number of records created, allowing you to test with a smaller dataset

## 2a. Running an archive-based crawl

Archive-based crawlers:

* bbc_archive
* cnn
* fox
* nbc
* wapo
* breitbart
* hill
* washtimes

These crawlers populate `archive_url`.

`bkr run --only archive_url` will process all archive_urls (converting them to archive_responses).

`bkr run --only archive_response` will process all archive_responses (converting them to <source>_urls).

Tip: Run `bkr show -w` in another terminal to see the database update in real time.

Tip: You can run both of these at once by passing `--only archive_url --only archive_response`.

## 2b. Running extractors

If you are using a non-archive-based crawler, the seed populated a beaker called <source>_urls.

If you are using an archive-based crawler, step 2a will have populated a beaker called <source>_urls.

`bkr run --only <source>_url` will process all <source>_urls (converting them to <source>_responses).

`bkr run --only <source>_response` will process all <source>_responses (converting them to articles).

