final: prev:
{
  python311 = prev.python311.override {
    packageOverrides = import ./python-overlay.nix {
      # inherit pkgs sources prjxray migen;
      # pythonPackages = python37Packages;
      pkgs = prev;
    };
  };
}
