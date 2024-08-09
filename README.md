# random_mullvad_endpoints

`random_mullvad_endpoints` reads JSON created by Mullvad's
`/relays/wireguard/v2` API endpoint and filters based on specified
criteria. These include regular expressions for the location and
provider. To present the final list of hostnames in a random order,
it uses weighted random sampling without replacement.

This tool is still under development. It's usable as is, but consider
the API unstable. When it's ready for public consumption, I'll
create a release.

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

## TODOs

- Documentation:
  - README.md (example usage)
- Features:
  - A way to print the entire list of hostnames rather than
    a subset of it.
- Packaging (flit?).
