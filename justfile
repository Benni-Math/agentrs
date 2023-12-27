publish:
    twine publish ./result/*.whl

build:
    nix build .

build-wheel:
    nix build .#wheel

build-wheel PLATFORM:
    nix build .#packages.{{PLATFORM}}.wheel
