{
  description = "Build fast ABMs in Python, with the help of Rust.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    crane = {
      url = "github:ipetkov/crane";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    fenix = {
      url = "github:nix-community/fenix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.rust-analyzer-src.follows = "";
    };

    flake-utils.url = "github:numtide/flake-utils";

    advisory-db = {
      url = "github:rustsec/advisory-db";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, crane, fenix, flake-utils, advisory-db, ... }:
    ({
      templates.default = {
        description = "Develop an ABM with `agentrs` - with easy image creation for running remotely.";
        path = ./template;
      };

      overlays.default = (final: prev:
        let
          agentrsOverride = { packageOverrides = (pyFinal: pyPrev: { agentrs = self.packages.${final.system}.default; }); };
        in
        {
          python3 = prev.python3.override agentrsOverride;
          python311 = prev.python311.override agentrsOverride;
          python311Full = prev.python311Full.override agentrsOverride;
        }
      );
    } // flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = (import nixpkgs {
          overlays = [
            fenix.overlays.default
            self.overlays.default
          ];
        #   config.allowUnfree = true;
          inherit system;
        });

        inherit (pkgs) lib;

        python = pkgs.python311;

        craneLib = crane.lib.${system};
        src = craneLib.cleanCargoSource (craneLib.path ./.);

        fenixToolchain = fenix.packages.${system}.complete;
        devToolchain = fenixToolchain.withComponents [
            "cargo"
            "llvm-tools"
            "rustc"
            "rust-src"
          ];

        craneLibLLvmTools = craneLib.overrideToolchain devToolchain;

        # Common arguments can be set here to avoid repeating them later
        commonArgs = {
          inherit src;
          # inherit pyproject;
          strictDeps = true;

          nativeBuildInputs = [
            pkgs.maturin
            python.pkgs.pip
            # pkgs.rust-analyzer-nightly
            devToolchain
          ];

          RUST_SRC_PATH="${fenixToolchain.rust-src}/lib/rustlib/src/rust/library/";

          buildInputs = [
            # Add additional build inputs here
            python.pkgs.numpy
          ] ++ lib.optionals pkgs.stdenv.isDarwin [
            # Additional darwin specific inputs can be set here
            pkgs.libiconv
          ];

          # Additional environment variables can be set directly
          # MY_CUSTOM_VAR = "some value";
        };

        # Build *just* the cargo dependencies, so we can reuse
        # all of that work (e.g. via cachix) when running in CI
        cargoArtifacts = craneLib.buildDepsOnly commonArgs;

        # Build the actual crate itself, reusing the dependency
        # artifacts from above.
        agentrs-crate = craneLib.mkCargoDerivation (commonArgs // {
          inherit cargoArtifacts;
          doCheck = false;
          buildPhaseCargoCommand = "maturin build --release --manylinux off";
          installPhaseCommand = "${python.pkgs.pip}/bin/pip install target/wheels/*.whl --no-index --prefix=$out --no-cache";
        });

        # Build wheel, for distribution through PyPi
        agentrs-wheel = craneLib.mkCargoDerivation (commonArgs // {
          inherit cargoArtifacts;
          doCheck = false;
          buildPhaseCargoCommand = "maturin build --release --manylinux off";
          installPhaseCommand = "mkdir -p $out && cp target/wheels/*.whl $out/";
        });

        agentrs-core-module = python.pkgs.toPythonModule agentrs-crate;

        agentrs-py = pkgs.python311Packages.buildPythonPackage {
            pname = "agentrs";
            version = "0.1.0";
            src = ./agentrs-py;
            nativeBuildInputs = with pkgs.python311Packages;  [
                setuptools
                wheel
            ];
            propagatedBuildInputs = [
                agentrs-core-module
            ];
            meta = with lib; {
                description = "Build an Agent-Based Model!";
                license = licenses.mit;
                homepage = "https://github.com/Benni-Math/agentrs";
                maintainers = [{
                    email = "benediktjens.arnarsson@gmail.com";
                    github = "Benni-Math";
                    githubId = 55165491;
                    name = "Benedikt Arnarsson";
                }];
            };
        };
      in
      {
        checks = {
          # Build the crate as part of `nix flake check` for convenience
          inherit agentrs-crate;

          # Run clippy (and deny all warnings) on the crate source,
          # again, resuing the dependency artifacts from above.
          #
          # Note that this is done as a separate derivation so that
          # we can block the CI if there are issues here, but not
          # prevent downstream consumers from building our crate by itself.
          agentrs-crate-clippy = craneLib.cargoClippy (commonArgs // {
            inherit cargoArtifacts;
            cargoClippyExtraArgs = "--all-targets -- --deny warnings";
          });

          agentrs-crate-doc = craneLib.cargoDoc (commonArgs // {
            inherit cargoArtifacts;
          });

          # Check formatting
          agentrs-crate-fmt = craneLib.cargoFmt {
            inherit src;
          };

          # Audit dependencies
          agentrs-crate-audit = craneLib.cargoAudit {
            inherit src advisory-db;
          };

          # Audit licenses
          agentrs-crate-deny = craneLib.cargoDeny {
            inherit src;
          };

          # Run tests with cargo-nextest
          # Consider setting `doCheck = false` on `agentrs-crate` if you do not want
          # the tests to run twice
          agentrs-crate-nextest = craneLib.cargoNextest (commonArgs // {
            inherit cargoArtifacts;
            partitions = 1;
            partitionType = "count";
          });
        };

        packages = {
          default = agentrs-py;
          crate = agentrs-crate;
          wheel = agentrs-wheel;
        } // lib.optionalAttrs (!pkgs.stdenv.isDarwin) {
          agentrs-crate-llvm-coverage = craneLibLLvmTools.cargoLlvmCov (commonArgs // {
            inherit cargoArtifacts;
          });
        };

        apps.default = flake-utils.lib.mkApp {
          drv = agentrs-crate;
        };

        devShells.default = craneLib.devShell {
          # Inherit inputs from checks.
          checks = self.checks.${system};

          # Additional dev-shell environment variables can be set directly
          # MY_CUSTOM_DEVELOPMENT_VAR = "something else";
          inherit (commonArgs) RUST_SRC_PATH;

          # Extra inputs can be added here; cargo and rustc are provided by default.
          packages = [
            python.pkgs.agentrs
            pkgs.just
            pkgs.twine
          ];
        };
      }));
}
