"""
Agentpy Sampling Module
Content: Sampling functions
"""

import itertools
import random
from typing import Any

import numpy as np

from .tools import AgentpyError


class Range:
    """ A range of parameter values
    that can be used to create a :class:`Sample`.

    Arguments:
        vmin (float, optional):
            Minimum value for this parameter (default 0).
        vmax (float, optional):
            Maximum value for this parameter (default 1).
        vdef (float, optional):
            Default value. Default value. If none is passed, `vmin` is used.
    """

    def __init__(self, vmin=0.0, vmax=1.0, vdef=None):
        self.vmin = vmin
        self.vmax = vmax
        self.vdef = vdef if vdef else vmin
        self.ints = False

    def __repr__(self):
        return f"Parameter range from {self.vmin} to {self.vmax}"


class IntRange(Range):
    """ A range of integer parameter values
    that can be used to create a :class:`Sample`.
    Similar to :class:`Range`,
    but sampled values will be rounded and converted to integer.

    Arguments:
        vmin (int, optional):
            Minimum value for this parameter (default 0).
        vmax (int, optional):
            Maximum value for this parameter (default 1).
        vdef (int, optional):
            Default value. If none is passed, `vmin` is used.
    """

    def __init__(self, vmin=0, vmax=1, vdef=None):
        self.vmin = int(round(vmin))
        self.vmax = int(round(vmax))
        self.vdef = int(round(vdef)) if vdef else vmin
        self.ints = True

    def __repr__(self):
        return f"Integer parameter range from {self.vmin} to {self.vmax}"


class Values:
    """ A pre-defined set of discrete parameter values
    that can be used to create a :class:`Sample`.

    Arguments:
        *args:
            Possible values for this parameter.
        vdef:
            Default value. If none is passed, the first passed value is used.
    """

    def __init__(self, *args, vdef=None):
        self.values = args
        self.vdef = vdef if vdef else args[0]

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"Set of {len(self.values)} parameter values"


class Sample:
    """ A sequence of parameter combinations
    that can be used for :class:`Experiment`.

    Arguments:

        parameters (dict):
            Dictionary of parameter keys and values.
            Entries of type :class:`Range` and :class:`Values`
            will be sampled based on chosen `method` and `n`.
            Other types wil be interpreted as constants.

        n (int, optional):
            Sampling factor used by chosen `method` (default None).

        method (str, optional):
            Method to use to create parameter combinations
            from entries of type :class:`Range`. Options are:

            - ``linspace`` (default):
              Arange `n` evenly spaced values for each :class:`Range`
              and combine them with given :class:`Values` and constants.
              Additional keyword arguments:

                - ``product`` (bool, optional):
                  Return all possible combinations (default True).
                  If False, value sets are 'zipped' so that the i-th
                  parameter combination contains the i-th entry of each
                  value set. Requires all value sets to have the same length.

        **kwargs: Additional keyword arguments for chosen `method`.

    """
    log: dict[str, Any] = {}

    def __init__(self, parameters, n=None,
                 method='linspace', **kwargs):

        self.log = {'type': method, 'n': n, 'randomized': False}
        self._sample = getattr(self, f"_{method}")(parameters, n, **kwargs)

    def __repr__(self):
        return f"Sample of {len(self)} parameter combinations"

    def __iter__(self):
        return iter(self._sample)

    def __len__(self):
        return len(self._sample)

    # Sampling methods ------------------------------------------------------ #

    def _assign_random_seeds(self, seed):
        rng = random.Random(seed)
        for parameters in self._sample:
            parameters['seed'] = rng.getrandbits(128)

    @staticmethod
    def _linspace(parameters, n, product=True):

        params = {}
        for k, v in parameters.items():
            if isinstance(v, Range):
                if n is None:
                    raise AgentpyError(
                        "Argument 'n' must be defined for Sample "
                        "if there are parameters of type Range.")
                if v.ints:
                    p_range = np.linspace(v.vmin, v.vmax+1, n)
                    p_range = [int(pv)-1 if pv == v.vmax+1 else int(pv)
                               for pv in p_range]
                else:
                    p_range = np.linspace(v.vmin, v.vmax, n)
                params[k] = p_range
            elif isinstance(v, Values):
                params[k] = v.values
            else:
                params[k] = [v]

        if product:
            # All possible combinations
            combos = list(itertools.product(*params.values()))
            sample = [dict(zip(params.keys(), c, strict=True)) for c in combos]
        else:
            # Parallel combinations (index by index)
            r = range(min([len(v) for v in params.values()]))
            sample = [{k: v[i] for k, v in params.items()} for i in r]

        return sample
