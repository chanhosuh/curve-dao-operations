# Curve DAO Operations

This repository aims to consolidate common on-chain DAO operations into a single accessible tool written in Python.  It provides a simple command-line interface that allows veCRV holders to create and decode on-chain executable proposals, while facilitating analytics on governance in the Curve DAO.

Such a CLI tool allows independence from a hosted website; after all, decentralisation goes beyond just network decentralisation: it more or less means democratic access to technology.


# Who needs this?

Curve DAO stakeholders have the ability to change the protocol in many ways.  From voting power gained from locking CRV into veCRV, stakeholders can create on-chain proposals to: 

- Allow or disable liquidity gauges from receiving CRV emissions
- Change liquidity pool parameters
- Request funds from the DAO Community Fund
- Add a smart contract to the whitelist to allow locking veCRV (only whitelisted contracts are allowed to lock veCRV)
- Changing pegkeeper debt ceiling
- Adding gauge types ...
- ... etc.


# Setup

## Environment Variables

Please setup access to IPFS using Infura at: [https://infura.io/](https://infura.io/)

1. `IPFS_PROJECT_ID`
2. `IPFS_PROJECT_SECRET`

Please setup access to Ethereum via Alchemy here: [https://www.alchemy.com/](https://www.alchemy.com/)

1. `WEB3_ALCHEMY_API_KEY`

If you're a power user that wants to use your own node, you'll need to setup `ape-config.yaml`:

```
hardhat:
  port: auto
  fork:
    ethereum:
      mainnet:
        upstream_provider: geth

geth:
  ethereum:
    mainnet:
      uri: <node url, e.g. http://localhost:9090>
```

## Installing the tool

The following is sufficient for installing all the dependencies (except one):

```console
$ python -m venv venv
$ source ./venv/bin/activate
$ pip install --upgrade pip
$ pip install .
```

**Note:** if you're planning on developing or customizing the codebase, you should do `pip install -e .`.  This will create an "editable" install.

The `ape-hardhat` plugin also requires `hardhat`, which should be npm installed using the `package-lock.json`:

```
npm install
```


# Available tools

Currently, the DAO operations tool grants the following:

#### `decode_executable`

This is a read-only tool that allows access to all users (they don't need to be a Curve Finance stakeholder) to decode an on-chain proposal.

Input args:

1. `vote_id`: The vote ID of an on-chain proposal
1. `type`: The voting type, `ownership` or `parameter`

An example of its usage is show in the following:

```console
$ decode_vote --type ownership --id 423
```

Output:

```console
[15:05:26] Decoding Ownership Vote: 423
[15:05:29] {'text': 'Add a gauge for the following pool:  cbETH/WETH on Base'}
[15:05:30] Call via agent: 0x40907540d8a6C65c637785e8f8B742ae6b0b9968
            ├─ To: 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
            ├─ Function: add_gauge
            └─ Inputs:
               ├─ addr: 0xE9c898BA654deC2bA440392028D2e7A194E6dc3e
               ├─ gauge_type: 5
               └─ weight: 0
```

# How to contribute:

The ultimate goal is to enable all major DAO operations in the CLI.  The main entrypoint is `curve_dao/scripts`, which has the primary commands for decoding and creating votes. 

In scope are:
- voting
- fee distribution
- pegkeeper updates
- crvUSD liquidations


## Pre-commit

For linting, the repo uses pre-commit hooks. Please install and use them via:

```
> pre-commit install
> pre-commit run --all-files
```

In order to contribute, please fork off of the `main` branch and make your changes there. Your commit messages should detail why you made your change in addition to what you did (unless it is a tiny change).

If you need to pull in any changes from `main` after making your fork (for example, to resolve potential merge conflicts), please avoid using `git merge` and instead, `git rebase` your branch

Please also include sufficient test cases, and sufficient docstrings. All tests must pass before a pull request can be accepted into `main`.

# Disclaimer

This is experimental software and is provided on an "as is" and "as available" basis. We do not give any warranties and will not be liable for any loss incurred through any use of this codebase.
