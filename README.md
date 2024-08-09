# random_mullvad_endpoints

`random_mullvad_endpoints` reads JSON created by Mullvad's
`/relays/wireguard/v2` API endpoint and filters based on specified
criteria. These include regular expressions for the location and
provider. To present the final list of hostnames in a random order,
it uses weighted random sampling without replacement.

## Example usage

First, clone the repository and download the necessary JSON data.

```shell
$ git clone https://github.com/maybebyte/random_mullvad_endpoints
$ cd random_mullvad_endpoints
$ curl -o mullvad-wireguard-relays.json https://api.mullvad.net/public/relays/wireguard/v2
```

Now `random_mullvad_endpoints` can process the JSON. Here is a basic
example that prints out only the hostnames of five active servers
anywhere in the world:

```shell
$ ./random_mullvad_endpoints.py -aN mullvad-wireguard-relays.json
us-mia-wg-103
de-dus-wg-002
fr-par-wg-004
nl-ams-wg-101
nl-ams-wg-001
```

It's also possible to send the data directly to
`random_mullvad_endpoints`:

```shell
$ curl -s https://api.mullvad.net/public/relays/wireguard/v2 | ./random_mullvad_endpoints.py -aN
es-vlc-wg-001
de-fra-wg-304
rs-beg-wg-101
sg-sin-wg-002
nl-ams-wg-006
```

More examples are available in the man page.

## Running tests

To run tests, execute this in the root of the project directory:

```shell
$ python3 -m pytest
```

## Documentation

You can use [mandoc](https://mandoc.bsd.lv/) to read the manual
page provided in the `docs` directory.

```shell
$ mandoc -l docs/random_mullvad_endpoints.1
```

There is also a generated Markdown file in the same directory so
you can [read the man page on
GitHub](https://github.com/maybebyte/random_mullvad_endpoints/blob/main/docs/random_mullvad_endpoints.md).
