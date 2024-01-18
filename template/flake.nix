{
  inputs = {
    nixpkgs.url = "nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";

    agentrs = {
      url = "github:Benni-Math/agentrs";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {self, nixpkgs, flake-utils, agentrs, ... }@inputs:
    let
      # Inherit helpers
      inherit (nixpkgs) lib;
      inherit (builtins)
          attrNames
          concatMap
          filter
          fromJson
          map
          readDir
          readFile;

      # Helpers:
      reqToPkgs = req: ps: (
        builtins.map (pyPkg: ps.${pyPkg}) req
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
        localOverlay = import ./nix/overlay.nix;
        pkgs = (import nixpkgs {
          overlays = [
            agentrs.overlays.default
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
            python311Packages.agentrs
            python311Packages.pytest
            # TODO: replace with marimo
            python311Packages.notebook
            just
            dive
          ];
        };

        packages.experimentSrc = experimentSrc;

        packages.docker = pkgs.dockerTools.buildLayeredImage {
          name = "abm-experiment";
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
            Volumes = {
              "/tmp/data": {};
            };
            WorkingDir = "/app";
          };
        };

        packages.default = derivation rec {
          name = "abm-experiment";
          builder = "${pkgs.bash}/bin/bash";
          args = [
            (pkgs.writeText "make-exp.sh"
              ''
              export PATH="$coreutils/bin"
              mkdir -p $out
              cp $image $out
              cp $runContainer/run-experiment.sh $out
              ''
            )
          ];
          inherit system;
          inherit (pkgs) coreutils;
          image = self.packages.${system}.docker;
          imageArchive = builtins.baseNameOf image;
          runContainer = pkgs.writeTextFile {
            name = "run-experiment.sh";
            text = ''
              #!/usr/bin/env bash
              if [[ ! -f "${lib.strings.removeSuffix ".gz" imageArchive}" ]]; then
                gzip -d ${imageArchive}
              fi
              docker load < *.tar
              docker run -t abm-experiment:latest
            '';
            executable = true;
            destination = "/run-experiment.sh";
          };

        };
      }
    );
}
