"""
Agentpy Output Module
Content: DataDict class for output data
"""

import json
import os
from os import listdir, makedirs
from os.path import getmtime, join
from pathlib import Path
from typing import Any, Self

import numpy as np
import pandas as pd

from .tools import AttrDict, make_list

#-------------------------------------------------------------#
#                          Constant                           #
#-------------------------------------------------------------#

PROJ_ROOT = Path(os.getcwd())
MODEL_OUTPUT = Path(os.environ.get('MODEL_OUTPUT_DIR') or (PROJ_ROOT / 'model_output'))

#-------------------------------------------------------------#
#                           Helpers                           #
#-------------------------------------------------------------#

def _last_exp_id(name, path):
    """Return the latest experiment (with the highest id)"""
    output_dirs= listdir(path)
    exp_dirs = [s for s in output_dirs if name in s]
    if exp_dirs:
        ids = [int(s.split('_')[-1]) for s in exp_dirs]
        return max(ids)
    else:
        return None

#-------------------------------------------------------------#
#                          Main Class                         #
#-------------------------------------------------------------#

class DataDict(AttrDict):
    """ Nested dictionary for output data of simulations.
    Items can be accessed like attributes.
    Attributes can differ from the standard ones listed below.

    Attributes:
        info (dict):
            Metadata of the simulation.
        parameters (DataDict):
            Simulation parameters.
        variables (DataDict):
            Recorded variables, separatedper object type.
        reporters (pandas.DataFrame):
            Reported outcomes of the simulation.
        sensitivity (DataDict):
            Sensitivity data, if calculated.
    """

    def __repr__(self, indent=False):
        rep = ""
        if not indent:
            rep += "DataDict {"
        i = '    ' if indent else ''
        for k, v in self.items():
            rep += f"\n{i}'{k}':"
            if isinstance(v, int | float | np.integer | np.floating):
                rep += f' {v} {type(v)}'
            elif isinstance(v, str):
                x0 = f"(length {len(v)})"
                x = f"...' {x0}" if len(v) > 20 else "'"
                rep += f" '{v[:30]}{x} {type(v)}"
            elif isinstance(v, pd.DataFrame):
                lv = len(list(v.columns))
                rv = len(list(v.index))
                rep += f" DataFrame with {lv} " \
                       f"variable{'s' if lv != 1 else ''} " \
                       f"and {rv} row{'s' if rv != 1 else ''}"
            elif isinstance(v, DataDict):
                rep += f"{v.__repr__(indent=True)}"
            elif isinstance(v, dict):
                lv = len(list(v.keys()))
                rep += f" Dictionary with {lv} key{'s' if lv != 1 else ''}"
            elif isinstance(v, list):
                lv = len(v)
                rep += f" List with {lv} entr{'ies' if lv != 1 else 'y'}"
            else:
                rep += f" Object of type {type(v)}"

        if not indent:
            rep += "\n}"

        return rep

    def _short_repr(self):
        len_ = len(self.keys())
        return f"DataDict {len_} entr{'y' if len_ == 1 else 'ies'}"

    def __eq__(self, other):
        """Check equivalence of two DataDicts."""
        if not isinstance(other, DataDict):
            return False
        for k, v in self.items():
            if k not in other:
                return False
            if isinstance(v, pd.DataFrame):
                if not self[k].equals(other[k]):
                    return False
            elif not self[k] == other[k]:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


    def arrange(self, variables=False, reporters=False,  # noqa: C901
                parameters=False, constants=False, obj_types=True, index=False):
        """ Combines and/or filters data based on passed arguments.

        Arguments:
            variables (bool or str or list of str, optional):
                Key or list of keys of variables to include in the dataframe.
                If True, all available variables are selected.
                If False (default), no variables are selected.
            reporters (bool or str or list of str, optional):
                Key or list of keys of reporters to include in the dataframe.
                If True, all available reporters are selected.
                If False (default), no reporters are selected.
            parameters (bool or str or list of str, optional):
                Key or list of keys of parameters to include in the dataframe.
                If True, all non-constant parameters are selected.
                If False (default), no parameters are selected.
            constants (bool, optional):
                Include constants if 'parameters' is True (default False).
            obj_types (str or list of str, optional):
                Agent and/or environment types to include in the dataframe.
                If True (default), all objects are selected.
                If False, no objects are selected.
            index (bool, optional):
                Whether to keep original multi-index structure (default False).

        Returns:
            pandas.DataFrame: The newly arranged dataframe.
        """
        dfv = dfm = dfp = df = None

        # Step 1: Variables
        if variables is not False:
            dfv = self._combine_vars(obj_types, variables)

        # Step 2: Measures
        if reporters is not False:
            dfm = self.reporters
            if reporters is not True:
                # make_list prevents conversion to pd.Series for single value
                dfm = dfm[make_list(reporters)]

        # Step 3: Parameters
        if parameters is True:
            dfp = self._combine_pars(constants=constants)
        elif parameters is not False:
            dfp = self._combine_pars()
            if dfp is not None:
                dfp = dfp[make_list(parameters)]

        # Step 4: Combine dataframes
        if dfv is not None and dfm is not None:
            index_keys = dfv.index.names
            dfm = dfm.reset_index()
            dfv = dfv.reset_index()
            df = pd.concat([dfm, dfv])
            df = df.set_index(index_keys)
        elif dfv is not None:
            df = dfv
        elif dfm is not None:
            df = dfm
        if dfp is not None:
            if df is None:
                df = dfp
            else:
                if df is not None and isinstance(df.index, pd.MultiIndex):
                    dfp = dfp.reindex(df.index, level='sample_id')
                df = pd.concat([df, dfp], axis=1)

        if df is None:
            return pd.DataFrame()

        # Step 6: Reset Index
        if not index:
            df = df.reset_index()

        return df

    # Some common variations of the arrange function
    def arrange_reporters(self):
        """ Common use case of :obj:`DataDict.arrange`
        with `reporters=True` and `parameters=True`. """
        return self.arrange(variables=False, reporters=True, parameters=True)

    def arrange_variables(self):
        """ Common use case of :obj:`DataDict.arrange`
        with `variables=True` and `parameters=True`. """
        return self.arrange(variables=True, reporters=False, parameters=True)


    def _combine_vars(self,
                      obj_types: Any = True,
                      var_keys: Any = True,
                      ) -> pd.DataFrame | None:
        """Return pandas dataframe with combined variables."""
        if 'variables' in self:
            vs = self['variables']
        else:
            return None

        if len(vs.keys()) == 1:
            return list(vs.values())[0]
        elif isinstance(vs, DataDict):
            df_dict = dict(vs)
        else:
            raise ValueError('Invalid DataDict')

        if var_keys is not True:
            df_dict = {k: v for k, v in df_dict.items()
                       if any(x in v.columns for x in make_list(var_keys))}

        if obj_types is not True:
            df_dict = {k: v for k, v in df_dict.items()
                       if k in make_list(obj_types)}

        model_type = self.info['model_type']
        if model_type in list(df_dict.keys()):
            df = df_dict[model_type]
            df['obj_id'] = 0
            indexes = list(df.index.names)
            indexes.insert(-1, 'obj_id')
            df = df.reset_index()
            df = df.set_index(indexes)
            df_dict[model_type] = df

        if df_dict == {}:
            return None

        # Create dataframe
        df = pd.concat(df_dict)
        df.index = df.index.set_names('obj_type', level=0)

        if var_keys is not True:
            df = df[make_list(var_keys)]

        return df

    def _dict_pars_to_df(self, dict_pars):
        """Convert a dictionary of parameters to dataframe."""
        n = self.info['sample_size'] if 'sample_size' in self.info else 1
        d = {k: [v] * n for k, v in dict_pars.items()}
        i = pd.Index(list(range(n)), name='sample_id')
        return pd.DataFrame(d, index=i)

    def _combine_pars(self, sample=True, constants=True) -> pd.DataFrame | None:
        """Return pandas dataframe with combined parameters."""
        if 'parameters' not in self:
            return None
        dfp = pd.DataFrame()
        if sample and 'sample' in self.parameters:
            dfp = self.parameters.sample.copy()
            if constants and 'constants' in self.parameters:
                for k, v in self.parameters.constants.items():
                    dfp[k] = v
        elif constants and 'constants' in self.parameters:
            dfp = self._dict_pars_to_df(self.parameters.constants)

        if dfp is None or dfp.empty is True:
            return None

        if 'seed' in dfp:
            del dfp['seed']

        return dfp

    # Saving and loading data ----------------------------------------------- #

    def save(self, exp_name=None, exp_id=None,  # noqa: C901
             path=MODEL_OUTPUT, display=True):
        """ Writes data to directory `{path}/{exp_name}_{exp_id}/`.

        Works only for entries that are of type :class:`DataDict`,
        :class:`pandas.DataFrame`, or serializable with JSON
        (int, float, str, dict, list). Numpy objects will be converted
        to standard objects, if possible.

        Arguments:
            exp_name (str, optional): Name of the experiment to be saved.
                If none is passed, `self.info['model_type']` is used.
            exp_id (int, optional): Number of the experiment.
                Note that passing an existing id can overwrite existing data.
                If none is passed, a new id is generated.
            path (str, optional): Target directory (default 'ap_output').
            display (bool, optional): Display saving progress (default True).
        """
        path = Path(path)
        # Create output director if it doesn't exist
        if not path.exists():
            makedirs(path)

        # Set exp_name
        if exp_name is None:
            if 'info' in self and 'model_type' in self.info:
                exp_name = self.info['model_type']
            else:
                exp_name = 'Unnamed'

        exp_name = exp_name.replace(" ", "_")

        # Set exp_id
        if exp_id is None:
            exp_id = _last_exp_id(exp_name, path)
            if exp_id is None:
                exp_id = 1
            else:
                exp_id += 1

        # Create new directory for output
        directory = f'{exp_name}_{exp_id}'
        path_dir = path / directory
        if directory not in listdir(path):
            makedirs(path_dir)

        # Save experiment data
        for key, output in self.items():

            if isinstance(output, pd.DataFrame):
                output.to_csv(path_dir / f'{key}.csv')
            elif isinstance(output, DataDict):
                for k, o in output.items():
                    if isinstance(o, pd.DataFrame):
                        o.to_csv(path_dir / f'{key}_{k}.csv')
                    elif isinstance(o, dict):
                        with open(path_dir / f'{key}_{k}.json', 'w') as fp:
                            # skipping bad keys - not the best practice
                            json.dump(o, fp, cls=NpEncoder, skipkeys=True)
            else:
                try:
                    with open(path_dir / f'{key}.json', 'w') as fp:
                        json.dump(output, fp, cls=NpEncoder)
                except TypeError as e:
                    print(f"Warning: Object '{key}' could not be saved."
                            f"(Reason: {e})")
                    os.remove(path_dir / f'{key}.json')

        if display:
            print(f"Data is saved to {path_dir}")


    @classmethod
    def load(cls, exp_name=None, exp_id=None, path=MODEL_OUTPUT, display=True) -> Self:
        """ Reads data from directory `{path}/{exp_name}_{exp_id}/`.

            Arguments:
                exp_name (str, optional): Experiment name.
                    If none is passed, the most recent experiment is chosen.
                exp_id (int, optional): Id number of the experiment.
                    If none is passed, the highest available id used.
                path (str, optional): Target directory (default 'model_output').
                display (bool, optional): Display loading progress (default True).

            Returns:
                DataDict: The loaded data from the chosen experiment.
        """
        return cls()._load(exp_name, exp_id, path, display)

    def _load(self,  # noqa: C901
              exp_name: str | None = None,
              exp_id: int | None = None,
              path=MODEL_OUTPUT,
              display=True,
              ) -> Self:
        path = Path(path)
        # Helper load
        def load_file(path: Path, file: str, display: bool):
            if display:
                print(f'Loading {file} - ', end='')
            i_cols = ['sample_id', 'iteration', 'obj_id', 't']
            ext = file.split(".")[-1]
            path = path / file
            try:
                if ext == 'csv':
                    # Convert .csv into DataFrame
                    obj = pd.read_csv(path)
                    index = [i for i in i_cols if i in obj.columns]
                    if index:
                        obj = obj.set_index(index)
                elif ext == 'json':
                    # Convert .json with json decoder
                    with open(path) as fp:
                        obj = json.load(fp)
                    # Convert dict to AttrDict
                    if isinstance(obj, dict):
                        obj = AttrDict(obj)
                else:
                    raise ValueError(f"File type '{ext}' not supported")

                if display:
                    print('Successful')

                return obj
            except Exception as e:
                print(f'Error: {e}')

        # Preparing experiment name
        if exp_name is None:
            exp_names = listdir(path)
            paths = [join(path, d) for d in exp_names]
            latest_exp = exp_names[paths.index(max(paths, key=getmtime))]
            exp_name = latest_exp.rsplit('_', 1)[0]

        exp_name = exp_name.replace(" ", "_")
        if exp_id is None:
            exp_id = _last_exp_id(exp_name, path)
            if exp_id is None:
                raise FileNotFoundError(f"No experiment found with "
                                        f"name '{exp_name}' in path '{path}'")

        path = path / f'{exp_name}_{exp_id}'
        if display:
            print(f'Loading from directory {path}')

        # Loading data
        for file in listdir(path):
            if 'variables_' in file:
                if 'variables' not in self:
                    self['variables'] = DataDict()
                ext = file.split(".")[-1]
                key = file[:-(len(ext) + 1)].replace('variables_', '')
                self['variables'][key] = load_file(path, file, display)
            elif 'parameters_' in file:
                ext = file.split(".")[-1]
                key = file[:-(len(ext) + 1)].replace('parameters_', '')
                if 'parameters' not in self:
                    self['parameters'] = DataDict()
                self['parameters'][key] = load_file(path, file, display)
            else:
                ext = file.split(".")[-1]
                key = file[:-(len(ext) + 1)]
                self[key] = load_file(path, file, display)

        return self



class NpEncoder(json.JSONEncoder):
    """Adds support for numpy number formats to json."""

    # By Jie Yang https://stackoverflow.com/a/57915246
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return super().default(obj)
