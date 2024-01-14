{
  description = "Build an Agent-Based Model!";

  inputs = {
    # nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    dream2nix.url = "github:nix-community/dream2nix";
    nixpkgs.follows = "dream2nix/nixpkgs";

    flake-utils.url = "github:numtide/flake-utils";
    agentrs.url = "github:Benni-Math/agentrs";
  };

  outputs = inputs@{ self, dream2nix, nixpkgs, flake-utils, agentrs, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      {
        # TODO: add Jupyter devShell
        # TODO: add Docker image build
        packages.default = dream2nix.lib.evalModules {
          packageSets.nixpkgs = import inputs.dream2nix.inputs.nixpkgs {
            overlays = [
                agentrs.overlays.default
            ];
            inherit system;
          };
          modules = [
            ./default.nix
            {
              paths.projectRoot = ./.;
              # can be changed to ".git" or "flake.nix" to get rid of .project-root
              paths.projectRootFile = "flake.nix";
              paths.package = ./.;
            }
          ];
        };

      });
}
