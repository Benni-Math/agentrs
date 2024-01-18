# { pkgs, sources, pythonPackages, prjxray, migen }:
{ pkgs }:

pyFinal: pyPrev:

# let
#   # Build a set with only the attributes listed in `names` from `attrs`.
#   intersectAttrs = names: attrs: getAttrs (intersectLists names (attrNames attrs)) attrs;
# in

{
  # This is required since python overrides do not compose
  agentrs = pkgs.python311.pkgs.agentrs;

  aiohttp = pkgs.callPackage ./python-pkgs/aiohttp (pkgs // pkgs.python311Packages);
#   pillow = if pkgs.stdenv.isDarwin then pkgs.callPackage ./python-pkgs/pillow.nix (pkgs // pkgs.python311Packages) else pyPrev.pillow;
}
