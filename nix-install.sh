#!/bin/env bash

# This script only works with `bash` or `zsh`

# Can change this to be most recent:
VERSION='2.19.2'

# Where we download Nix from:
URL="https://releases.nixos.org/nix/nix-${VERSION}/install"

# Enable flakes by default
CONFIGURATION="
extra-experimental-features = nix-command flakes repl-flake
extra-trusted-users = ${USER}
"

# Run installation, with channels disabled by default
sh <(curl --location "${URL}") \
        --no-channel-add \
        --nix-extra-conf-file <(<<< "${CONFIGURATION}")
