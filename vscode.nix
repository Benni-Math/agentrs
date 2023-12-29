{ lib, pkgs }:

let
  python = pkgs.python310;

  myvscode = pkgs.vscode-with-extensions.override {
    vscodeExtensions = with pkgs.vscode-extensions; [
      ms-python.python
      ms-toolsai.jupyter
      ms-toolsai.jupyter-keymap
      ms-toolsai.jupyter-renderers
      ms-toolsai.vscode-jupyter-cell-tags
      ms-toolsai.vscode-jupyter-slideshow
    ];
  };

  pythonRunPackages = with python.pkgs;[
    python
    ipywidgets
    jupyter
    ipykernel
    plotly
  ];

  pythonDevPackages = with python.pkgs;[
    black
    flake8
    pylint
    setuptools
  ] ++ pythonRunPackages;

  venv = python.withPackages (ps: pythonDevPackages);
in
{
  inherit python pythonRunPackages pythonDevPackages venv;

  shell = pkgs.mkShell {
    buildInputs = pythonDevPackages ++ [ myvscode ];
  };
}
