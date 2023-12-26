{
  description = "Build a cargo project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    agentrs.url = "github:Benni-Math/agentrs";

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, pyproject-nix, agentrs, flake-utils, ... }:
    let
      pkgsForSystem = system: import nixpkgs {
        # if you have additional overlays, you may add them here
        overlays = [
          agentrs.overlays.default
        ];
        inherit system;
      };
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = pkgsForSystem system;

        python = pkgs.python311Full;

        project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
      in
      {
        # TODO: add Jupyter devShell
        devShells.default =
          let
            # Returns a function that can be passed to `python.withPackages`
            arg = project.renderers.withPackages { inherit python; };

            # Returns a wrapped environment (virtualenv like) with all our packages
            pythonEnv = python.withPackages arg;
          in
          pkgs.mkShell {
            packages = [
              pythonEnv
              pkgs.agentrs
              pkgs.just
            ];
          };

        # TODO: add Docker image build
        packages.default =
          let
            # Returns an attribute set that can be passed to `buildPythonPackage`.
            attrs = project.renderers.buildPythonPackage { inherit python; };
          in
          python.pkgs.buildPythonPackage (attrs // {
            env.CUSTOM_ENVVAR = "hello";
          });
    
      });
}
