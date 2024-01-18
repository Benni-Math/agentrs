"""
Agentpy Experiment Module
Content: Experiment class
"""

from datetime import datetime, timedelta
import sys

from joblib import Parallel, delayed
import pandas as pd
from tqdm import tqdm

from .datadict import DataDict
from .sample import Sample
from .tools import make_list, tqdm_joblib


class Experiment:
    """ Experiment that can run an agent-based model
    over for multiple iterations and parameter combinations
    and generate combined output data.

    Arguments:
        model (type):
            The model class for the experiment to use.
        sample (dict or list of dict or Sample, optional):
            Parameter combination(s) to test in the experiment (default None).
        iterations (int, optional):
            How often to repeat every parameter combination (default 1).
        record (bool, optional):
            Keep the record of dynamic variables (default False).
        **kwargs:
            Will be forwarded to all model instances created by the experiment.

    Attributes:
        output(DataDict): Recorded experiment data
    """

    def __init__(self, model_class, sample=None, iterations=1,
                 record=False, randomize=True, **kwargs):
        self.model = model_class
        self.output = DataDict()
        self.iterations = iterations
        self.record = record
        self._model_kwargs = kwargs
        self.name = model_class.__name__

        # Prepare sample
        if isinstance(sample, Sample):
            self.sample = list(sample)
            self._sample_log = sample.log
        else:
            self.sample = make_list(sample, keep_none=True)
            self._sample_log = None

        # Prepare runs
        len_sample = len(self.sample)
        iter_range = range(iterations) if iterations > 1 else [None]
        sample_range = range(len_sample) if len_sample > 1 else [None]
        self.run_ids = [(sample_id, iteration)
                        for sample_id in sample_range
                        for iteration in iter_range]
        self.n_runs = len(self.run_ids)

        # Prepare output
        self.output.info = {
            'model_type': model_class.__name__,
            'time_stamp': str(datetime.now()),
            'python_version': sys.version[:5],
            'experiment': True,
            'scheduled_runs': self.n_runs,
            'completed': False,
            'random': randomize,
            'record': record,
            'sample_size': len(self.sample),
            'iterations': iterations
        }
        self._parameters_to_output()

    def _parameters_to_output(self):
        """Document parameters (separately for fixed & variable)."""
        df = pd.DataFrame(self.sample)
        df.index.rename('sample_id', inplace=True)
        fixed_pars = {}
        for col in df.columns:
            s = df[col]
            if len(s.map(str).unique()) == 1:
                fixed_pars[s.name] = df[col][0]
                df.drop(col, inplace=True, axis=1)
        self.output['parameters'] = DataDict()
        if fixed_pars:
            self.output['parameters']['constants'] = fixed_pars
        if not df.empty:
            self.output['parameters']['sample'] = df
        if self._sample_log:
            self.output['parameters']['log'] = self._sample_log

    @staticmethod
    def _add_single_output_to_combined(single_output, combined_output):
        """Append results from single run to combined output.
        Each key in single_output becomes a key in combined_output.
        DataDicts entries become dicts with lists of values.
        Other entries become lists of values. """
        for k, v in single_output.items():
            if k in ['parameters', 'info']:
                continue
            if isinstance(v, DataDict):
                if k not in combined_output:
                    combined_output[k] = {}
                for obj_type, obj_df in single_output[k].items():
                    if obj_type not in combined_output[k]:
                        combined_output[k][obj_type] = []
                    combined_output[k][obj_type].append(obj_df)
            else:
                if k not in combined_output:
                    combined_output[k] = []
                combined_output[k].append(v)

    def _combine_dataframes(self, combined_output):
        """ Combines data from combined output.
        Dataframes are combined with concat.
        Dicts are transformed to DataDict.
        Other objects are kept as original.
        Combined data is written to self.output. """
        for key, values in combined_output.items():
            if values and all(isinstance(value, pd.DataFrame) for value in values):
                self.output[key] = pd.concat(values)
            elif isinstance(values, dict):
                self.output[key] = DataDict()
                for sk, sv in values.items():
                    if all(isinstance(v, pd.DataFrame) for v in sv):
                        self.output[key][sk] = pd.concat(sv)
                    else:
                        self.output[key][sk] = sv
            elif key != 'info':
                self.output[key] = values

    def _single_sim(self, run_id):
        """Perform a single simulation."""
        sample_id = 0 if run_id[0] is None else run_id[0]
        parameters = self.sample[sample_id]
        model = self.model(parameters, _run_id=run_id, **self._model_kwargs)
        results = model.run(display=False)
        if 'variables' in results and self.record is False:
            del results['variables']
        return results

    def run(self, n_jobs=1, display=True, **kwargs):
        """
        Perform the experiment.

        The simulation will run the model once for each set of parameters
        and will repeat this process for the set number of iterations.
        Simulation results will be stored in `Experiment.output`.
        Parallel processing is supported based on :func:`joblib.Parallel`.

        Arguments:
            n_jobs (int, optional):
                Number of processes to run in parallel (default 1).
                If 1, no parallel processing is used. If -1, all CPUs are used.
                Will be forwarded to :func:`joblib.Parallel`.
            pool (multiprocessing.Pool, optional):
                [This argument is depreciated.
                Please use 'n_jobs' instead.]
                Pool of active processes for parallel processing.
                If none is passed, normal processing is used.
            display (bool, optional):
                Display simulation progress (default True).
            **kwargs:
                Additional keyword arguments for :func:`joblib.Parallel`.

        Returns:
            DataDict: Recorded experiment data.

        Examples:

            To run a normal experiment::

                exp = ap.Experiment(MyModel, parameters)
                results = exp.run()

            To use parallel processing on all CPUs with status updates::

                exp = ap.Experiment(MyModel, parameters)
                results = exp.run(n_jobs=-1, verbose=10)
        """
        if display:
            n_runs = self.n_runs
            print(f"Scheduled runs: {n_runs}")
        t0 = datetime.now()
        combined_output = {}

        if n_jobs != 1:
            with tqdm_joblib(tqdm(desc="Experiment progress", total=self.n_runs)):
                output_list = Parallel(n_jobs=n_jobs, **kwargs)(
                    delayed(self._single_sim)(i) for i in self.run_ids
                )
            for single_output in make_list(output_list):
                self._add_single_output_to_combined(
                    single_output,
                    combined_output
                )
        else:
            i = -1
            for run_id in self.run_ids:
                self._add_single_output_to_combined(
                    self._single_sim(run_id), combined_output
                )
                if display:
                    i += 1
                    td = (datetime.now() - t0).total_seconds()
                    te = timedelta(seconds=int(td / (i + 1) * (self.n_runs - i - 1)))
                    print(f"\rCompleted: {i + 1}, estimated time remaining: {te}",
                          end='')
            if display:
                print("")

        self._combine_dataframes(combined_output)
        self.end()
        self.output.info['completed'] = True
        self.output.info['run_time'] = ct = str(datetime.now() - t0)

        if display:
            print(f"Experiment finished\nRun time: {ct}")

        return self.output

    # Overwrite for final calculations and reporting
    def end(self):
        """ Defines the experiment's actions after the last simulation.
        Can be overwritten for final calculations and reporting."""
        pass
