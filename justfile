publish:
    twine publish ./result/*.whl

build:
    nix build .

build-wheel:
    nix build .#wheel

build-wheel PLATFORM:
    nix build .#packages.{{PLATFORM}}.wheel

develop:
    nix develop --command zsh

generate-ci:
    maturin generate-ci github
