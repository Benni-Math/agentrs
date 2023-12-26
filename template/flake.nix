{
  description = "Build a cargo project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    agentrs = {
      url = "github:Benni-Math/agentrs";
      inputs.nixpkgs.follows = "nixpkgs";
    }
  };

  outputs = { self, nixpkgs, pyproject-nix, agentrs, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        inherit (pkgs) lib;

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
              agentrs
              pkgs.just
            ]
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
