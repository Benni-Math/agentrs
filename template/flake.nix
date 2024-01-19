{
  inputs = {
    nixpkgs.url = "nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";

    agentrs = {
      url = "github:Benni-Math/agentrs";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    marimo = {
      url = "github:Benni-Math/marimo";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {self, nixpkgs, flake-utils, agentrs, marimo, ... }@inputs:
    let
      # Inherit helpers
      inherit (nixpkgs) lib;
      inherit (builtins) map;

      # Helpers:
      reqToPkgs = req: ps: (
        map (pyPkg: ps.${pyPkg}) req
      );

      # Requirements:
      dockerReq = [ "agentrs" ];
      devReq = dockerReq ++ [ "seaborn" ];

      # Create package lists:
      devPkgs = reqToPkgs devReq;
      dockerPkgs = reqToPkgs dockerReq;
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        dockerImageName = "abm-experiment";
        dockerComposeName = "abm-experiment-service";

        localOverlay = import ./nix/overlay.nix;
        pkgs = (import nixpkgs {
          overlays = [
            agentrs.overlays.default
            marimo.overlays.default
            localOverlay
          ];
          inherit system;
        });

        pythonEnv = pkgs.python311.withPackages devPkgs;
        dockerEnv = pkgs.python311.withPackages dockerPkgs;

        experimentSrc = pkgs.stdenv.mkDerivation {
          name = "experiment-src";
          src = lib.fileset.toSource {
            root = ./.;
            fileset = lib.fileset.unions [
              ./runexp.py
              ./src
            ];
          };
          phases = [ "unpackPhase" "installPhase" ];
          installPhase = ''
            mkdir -p $out/app
            cp -r $src/. $out/app/
          '';
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            pythonEnv
            # ruff
            # mypy
            pkgs.marimo
            python311Packages.agentrs
            python311Packages.pytest
            just
            dive
          ];
        };

        packages.experimentSrc = experimentSrc;

        packages.docker = pkgs.dockerTools.buildLayeredImage {
          name = dockerImageName;
          tag = "latest";
          contents = pkgs.buildEnv {
            name = "image-root";
            paths = [
              # Add python environment:
              dockerEnv
              # Copy over source:
              self.packages.${system}.experimentSrc
            ];
            pathsToLink = [
              # Capture python environment
              "/bin"
              # Capture what we need from source
              "/app"
            ];
          };
          config =  {
            Entrypoint = [ "/bin/python" "runexp.py" ];
            Env = [
              "MODEL_INPUT_DIR=/data/model_input"
              "MODEL_OUTPUT_DIR=/data/model_output"
            ];
            WorkingDir = "/app";
          };
        };

        packages.default = derivation rec {
          name = "${dockerImageName}-zip";
          builder = "${pkgs.bash}/bin/bash";
          args = [
            (pkgs.writeText "make-exp.sh"
              ''
              export PATH="$coreutils/bin"
              mkdir -p $out
              cp $image $out
              cp $runContainer/run-experiment.sh $out
              cp $composeYaml/compose.yaml $out
              ''
            )
          ];
          inherit system;
          inherit (pkgs) coreutils;
          image = self.packages.${system}.docker;
          imageArchive = builtins.baseNameOf image;
          composeYaml = pkgs.writeTextFile {
            name = "compose.yaml";
            text = ''
              version: '3.3'
              services:
                ${dockerComposeName}:
                  image: ${dockerImageName}:latest
                  volumes:
                    - './model_input:/data/model_input'
                    - './model_output:/data/model_output'
            '';
            destination = "/compose.yaml";
          };
          runContainer = pkgs.writeTextFile {
            name = "run-experiment.sh";
            text = ''
              #!/usr/bin/env bash
              if [[ ! -f "${lib.strings.removeSuffix ".gz" imageArchive}" ]]; then
                gzip -d ${imageArchive}
              fi
              docker load < *.tar
              exec docker compose run --rm -it ${dockerComposeName}
            '';
            executable = true;
            destination = "/run-experiment.sh";
          };

        };
      }
    );
}
