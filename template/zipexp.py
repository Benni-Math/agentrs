"""
Create an experiment zipfile.
"""
import os
from pathlib import Path
import sys
import zipfile

# TODO: replace name (or create method to generate names)
exp_dir = Path(__file__).parent / 'experiment_zipfiles'
expz_path = exp_dir / 'my-experiment.zip'

def zipdir(ziph, path, prefix=''):
    """Write the contents of a directory to a zipfile handle."""
    dirname = os.path.join(path, '..') if prefix != '..' else path
    for root, _dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            dirpath = os.path.relpath(filepath, dirname)
            arcname = os.path.join(prefix, dirpath) if prefix != '..' else dirpath
            ziph.write(filepath, arcname)

with zipfile.ZipFile(expz_path, 'w', zipfile.ZIP_DEFLATED, strict_timestamps=False) as expz:
    # Place the Docker image and script into the root
    zipdir(expz, 'result', prefix='..')
    # TODO: replace this with more fine-grained zipping
    zipdir(expz, 'model_input')

sys.exit(0)
