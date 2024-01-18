"""
Agentpy Tools Module
Content: Errors, generators, and base classes
"""

import contextlib
from typing import Any, Generic, TypedDict, TypeVar

import joblib
from numpy import ndarray

TDict = TypeVar('TDict', bound=TypedDict, covariant=True)

class AgentpyError(Exception):
    pass


def make_none(*args, **kwargs):
    return None


class InfoStr(str):
    """ String that is displayed in user-friendly format. """
    def __repr__(self):
        return self


def make_matrix(shape, loc_type=make_none, list_type=list, pos=None):
    """ Returns a nested list with given shape and class instance. """

    if pos is None:
        pos = ()

    if len(shape) == 1:
        return list_type([loc_type(pos+(i,))
                          for i in range(shape[0])])
    return list_type([make_matrix(shape[1:], loc_type, list_type, pos+(i,))
                      for i in range(shape[0])])


def make_list(element: Any, keep_none=False):
    """ Turns element into a list of itself
    if it is not of type list or tuple. """

    if element is None and not keep_none:
        element = []  # Convert none to empty list
    if not isinstance(element, list | tuple | set | ndarray):
        element = [element]
    elif isinstance(element, tuple | set):
        element = list(element)

    return element


def param_tuples_to_salib(param_ranges_tuples):
    """ Convert param_ranges to SALib Format """

    param_ranges_salib = {
        'num_vars': len(param_ranges_tuples),
        'names': list(param_ranges_tuples.keys()),
        'bounds': []
    }

    for _var_key, var_range in param_ranges_tuples.items():
        param_ranges_salib['bounds'].append([var_range[0], var_range[1]])

    return param_ranges_salib


class AttrDict(dict):
    """ Dictionary where attribute calls are handled like item calls.

    Examples:

        >>> ad = ap.AttrDict()
        >>> ad['a'] = 1
        >>> ad.a
        1

        >>> ad.b = 2
        >>> ad['b']
        2
    """

    def __init__(self, *args, **kwargs):
        if args == (None, ):
            args = ()  # Empty tuple
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            # Important for pickle to work
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        self.__setitem__(name, value)

    def __delattr__(self, item):
        del self[item]

    def _short_repr(self):
        len_ = len(self.keys())
        return f"AttrDict ({len_} entr{'y' if len_ == 1 else 'ies'})"


class TypedAttrDict(AttrDict, Generic[TDict]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """
    Context manager to patch joblib to report into tqdm progress bar given as argument.

    https://stackoverflow.com/a/58936697
    """
    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        """Monkey-patch class for tqdm BatchCompletionCallback."""

        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()
