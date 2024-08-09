RANDOM\_MULLVAD\_ENDPOINTS(1) - General Commands Manual

# NAME

**random\_mullvad\_endpoints** - extracts data corresponding to random Mullvad VPN endpoints

# SYNOPSIS

**random\_mullvad\_endpoints**
\[**-ahoN**]
\[**-l**&nbsp;*regexp*]
\[**-n**&nbsp;*integer*]
\[**-p**&nbsp;*regexp*]
\[*file*]

# DESCRIPTION

The
**random\_mullvad\_endpoints**
utility processes JSON provided by Mullvad's API and extracts data from
it. By default, data is extracted for 5 random endpoints. Endpoints are
selected using weighted random sampling without replacement.

If
*file*
is a single dash
('-')
or absent,
**random\_mullvad\_endpoints**
reads from the standard input.

The options are as follows:

**-a**

> Only include active Mullvad endpoints.

**-A**

> Include all matching Mullvad endpoints, rather than a limited number.
> This means that
> **-n**
> will be ignored.

**-h**

> Print usage information and exit.

**-l** *regexp*

> Only include endpoints with locations that match the given regular
> expression.

**-n** *integer*

> Number of endpoints to select and return data for (defaults to 5).
> Will be ignored if
> **-A**
> was provided.

**-N**

> Print the hostname of each endpoint rather than the full JSON data.

**-o**

> Only include Mullvad endpoints that are owned by Mullvad. Ownership
> means servers that Mullvad has physical control of, as opposed to
> servers that are rented.

**-p** *regexp*

> Only include providers that match the given regular expression.

# EXIT STATUS

The
**random\_mullvad\_endpoints**
utility exits 0 on success, and &gt;0 if an error occurs.

# EXAMPLES

Randomly select 5 Mullvad VPN endpoints from the mullvad.json file that
are active and located in the United States. Print out the corresponding
JSON.

	$ random_mullvad_endpoints -al `^us-[a-z]{3}$' mullvad.json

Randomly select 10 Mullvad VPN endpoints from anywhere in the world,
reading from STDIN. Print out only the hostnames.

	$ cat mullvad.json | random_mullvad_endpoints -n 10 -N

Randomly select 5 Mullvad VPN endpoints from anywhere in the world, but
they must be owned by Mullvad and the provider must be 31173. Print out
the corresponding JSON.

	$ random_mullvad_endpoints -op `^31173$' mullvad.json

Print out all endpoint hostnames in a random order.

	$ random_mullvad_endpoints -AN mullvad.json

# SEE ALSO

[Mullvad API Documentation](https://api.mullvad.net/public/documentation/)

[WireGuard Relays](https://api.mullvad.net/public/relays/wireguard/v2)

# AUTHORS

Written and maintained by
Ashlen &lt;[dev@anthes.is](mailto:dev@anthes.is)&gt;.

# CAVEATS

Weights less than or equal to 0 are handled by treating them as if they
were actually 1. This is for two reasons, both ultimately related to the
algorithm chosen to handle weighted sampling without replacement
(Efraimidis and Spirakis).

The first reason is that a weight of zero will lead to a division by
zero error.

The second reason is that negative weights mess up the weighting system.
Due to the math involved, negative weights would always end up being
prioritized over any positive weight, which is unlikely to be the
desired outcome.
