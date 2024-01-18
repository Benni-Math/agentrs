{ lib
, stdenv
, buildPythonPackage
, pythonOlder
, fetchPypi
, isPyPy
, defusedxml, olefile, freetype, libjpeg, zlib, libtiff, libwebp, libxcrypt, tcl, lcms2, tk, libX11
, libxcb, openjpeg, libimagequant, pyroma, numpy, pytestCheckHook, setuptools
# for passthru.tests
, imageio, matplotlib, pilkit, pydicom, reportlab, ...
}@args:

let
  metadata = rec {
    pname = "pillow";
    # version = 10.1.0; # <- some tests fail!
    version = "10.0.1";
    format = "pyproject";

    disabled = pythonOlder "3.8";

    src = fetchPypi {
      pname = "Pillow";
      inherit version;
      # For reference: https://www.srihash.org
      # With input: https://files.pythonhosted.org/packages/64/9e/7e638579cce7dc346632f020914141a164a872be813481f058883ee8d421/Pillow-10.0.1.tar.gz
      hash = "sha256-1ylnsGvpMA/tXPvItbr87sSL983H2rZrHSVJA1KHGR0=";
    };

    passthru.tests = {
      inherit imageio matplotlib pilkit pydicom reportlab;
    };

    meta = with lib; {
      homepage = "https://python-pillow.org/";
      description = "The friendly PIL fork (Python Imaging Library)";
      longDescription = ''
        The Python Imaging Library (PIL) adds image processing
        capabilities to your Python interpreter.  This library
        supports many file formats, and provides powerful image
        processing and graphics capabilities.
      '';
      license = licenses.hpnd;
      maintainers = with maintainers; [ goibhniu prikhi ];
    };
  };
in

with metadata;

buildPythonPackage rec {
  inherit (metadata) pname version format src meta passthru;

  # Disable imagefont tests, because they don't work well with infinality:
  # https://github.com/python-pillow/Pillow/issues/1259
  postPatch = ''
    rm Tests/test_imagefont.py
  '';

  disabledTests = [
    # Code quality mismathch 9 vs 10
    "test_pyroma"

    # pillow-simd
    "test_roundtrip"
    "test_basic"
    "test_custom_metadata"
  ] ++ lib.optionals stdenv.isDarwin [
    # Disable darwin tests which require executables: `iconutil` and `screencapture`
    "test_grab"
    "test_grabclipboard"
    "test_save"
  ];

  propagatedBuildInputs = [ olefile ]
    ++ lib.optionals (lib.versionAtLeast version "8.2.0") [ defusedxml ];

  nativeCheckInputs = [ pytestCheckHook pyroma numpy ];

  nativeBuildInputs = [ setuptools ];

  buildInputs = [ freetype libjpeg openjpeg libimagequant zlib libtiff libwebp libxcrypt tcl lcms2 ]
    ++ lib.optionals (lib.versionAtLeast version "7.1.0") [ libxcb ]
    ++ lib.optionals (isPyPy) [ tk libX11 ];

  # NOTE: we use LCMS_ROOT as WEBP root since there is not other setting for webp.
  # NOTE: The Pillow install script will, by default, add paths like /usr/lib
  # and /usr/include to the search paths. This can break things when building
  # on a non-NixOS system that has some libraries installed that are not
  # installed in Nix (for example, Arch Linux has jpeg2000 but Nix doesn't
  # build Pillow with this support). We patch the `disable_platform_guessing`
  # setting here, instead of passing the `--disable-platform-guessing`
  # command-line option, since the command-line option doesn't work when we run
  # tests.
  preConfigure = let
    libinclude' = pkg: ''"${pkg.out}/lib", "${pkg.out}/include"'';
    libinclude = pkg: ''"${pkg.out}/lib", "${pkg.dev}/include"'';
  in ''
    sed -i "setup.py" \
        -e 's|^FREETYPE_ROOT =.*$|FREETYPE_ROOT = ${libinclude freetype}|g ;
            s|^JPEG_ROOT =.*$|JPEG_ROOT = ${libinclude libjpeg}|g ;
            s|^JPEG2K_ROOT =.*$|JPEG2K_ROOT = ${libinclude openjpeg}|g ;
            s|^IMAGEQUANT_ROOT =.*$|IMAGEQUANT_ROOT = ${libinclude' libimagequant}|g ;
            s|^ZLIB_ROOT =.*$|ZLIB_ROOT = ${libinclude zlib}|g ;
            s|^LCMS_ROOT =.*$|LCMS_ROOT = ${libinclude lcms2}|g ;
            s|^TIFF_ROOT =.*$|TIFF_ROOT = ${libinclude libtiff}|g ;
            s|^TCL_ROOT=.*$|TCL_ROOT = ${libinclude' tcl}|g ;
            s|self\.disable_platform_guessing = None|self.disable_platform_guessing = True|g ;'
    export LDFLAGS="$LDFLAGS -L${libwebp}/lib"
    export CFLAGS="$CFLAGS -I${libwebp}/include"
  '' + lib.optionalString (lib.versionAtLeast version "7.1.0") ''
    export LDFLAGS="$LDFLAGS -L${libxcb}/lib"
    export CFLAGS="$CFLAGS -I${libxcb.dev}/include"
  '' + lib.optionalString stdenv.isDarwin ''
    # Remove impurities
    substituteInPlace setup.py \
      --replace '"/Library/Frameworks",' "" \
      --replace '"/System/Library/Frameworks"' ""
  '';
}
