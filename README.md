# AgentPy-rs

A Rust based implementation of the AgentPy library,
to speed up both development and runtime of agent-based models.

<!-- https://github.com/iWeltAG/zucker/blob/main/flake.nix -->

## Prerequisites

To quickly start a new project, all that you need is [Nix](https://nixos.org) (only the package manager, not the OS).

To install, simply run `sh nix-install.sh` (this will also go through some extra setup steps for you).

If you are on MacOS, please see [how to setup a linux-builder](https://nixos.org/manual/nixpkgs/unstable/#sec-darwin-builder) (and don't forget to `nix run nixpkgs#darwin.linux-builder` whenever you build with Nix)

## User guide

Assume that you have Nix installed, it's as easy as:

```sh
mkdir my-abm
cd my-abm
nix flake init -t github:Benni-Math/agentrs
```

Then, you can start developing with `nix develop`, or open a Jupyter Notebook with `nix run .`, or build a Docker image for your model with `nix build .#docker`.