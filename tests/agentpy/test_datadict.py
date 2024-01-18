import os
from pathlib import Path
import shutil

import numpy as np
import pytest

import agentrs.agentpy as ap

TEST_DIR = Path('test_ap_output')

def test_combine_vars():

    model = ap.Model()
    model.record('test', 1)
    results = model.run(1, display=False)
    model_vars = results._combine_vars()
    assert model_vars is not None
    assert model_vars.shape == (1, 1)

    model = ap.Model()
    agents = ap.AgentList(model, 1)
    agents.record('test', 1) # type: ignore
    results = model.run(1, display=False)
    model_vars = results._combine_vars()
    assert model_vars is not None
    assert model_vars.shape == (1, 1)

    model = ap.Model()
    agents = ap.AgentList(model, 1)
    model.record('test', 1)
    agents.record('test', 2) # type: ignore
    results = model.run(1, display=False)
    model_vars = results._combine_vars()
    assert model_vars is not None
    assert model_vars.shape == (2, 1)

    model = ap.Model()
    agents = ap.AgentList(model, 1)
    model.record('test', 1)
    agents.record('test', 2) # type: ignore
    results = model.run(1, display=False)
    model_vars = results._combine_vars(obj_types="Model")
    assert model_vars is not None
    assert model_vars.shape == (1, 1)

    model = ap.Model()
    agents = ap.AgentList(model, 1)
    model.record('test', 1)
    agents.record('test', 2) # type: ignore
    results = model.run(1, display=False)
    assert results._combine_vars(obj_types="Doesn't exist") is None

    model = ap.Model()
    results = model.run(1, display=False)
    assert results._combine_vars() is None
    assert results._combine_pars() is None

    model = ap.Model({'test': 1})
    results = model.run(1, display=False)
    assert results._combine_pars(constants=False) is None


repr = """DataDict {
'info': Dictionary with 11 keys
'parameters':
    'constants': Dictionary with 2 keys
    'sample': DataFrame with 1 variable and 10 rows
    'log': Dictionary with 3 keys
'variables':
    'Agent': DataFrame with 1 variable and 10 rows
    'MyModel': DataFrame with 1 variable and 10 rows
'reporters': DataFrame with 1 variable and 10 rows
}"""


class MyModel(ap.Model):
    def step(self):
        self.report('x', self.p.x)
        self.agents = ap.AgentList(self, 1)
        self.agents.record('id')    # type: ignore
        self.record('id')
        self.stop()


def test_repr():
    param_ranges = {'x': ap.Range(0., 1.), 'y': 1, 'report_seed': False}
    sample = ap.Sample(param_ranges, n=10)
    results = ap.Experiment(MyModel, sample, record=True).run()
    assert results.__repr__() == repr


def test_testing_model(model_results, exp_results):
    type_list = ['AgentType1', 'AgentType2', 'EnvType3', 'EnvType4']
    assert list(model_results.variables.keys()) == type_list
    assert list(exp_results.variables.keys()) == type_list


def _arrange_things(results):

    return (results.arrange(variables='x'),
            results.arrange(variables=['x']),
            results.arrange(variables=['x', 'y']),
            results.arrange(variables='z'),
            results.arrange(parameters='px'),
            results.arrange(reporters='m_key'),
            results.arrange(variables=True,
                            parameters=True,
                            reporters=True),
            results.arrange())


def test_datadict_arrange_for_single_run(model_results: ap.DataDict):

    results = model_results
    data = _arrange_things(results)
    x_data, x_data2, xy_data, z_data, p_data, m_data, all_data, no_data = data

    assert x_data.equals(x_data2)
    assert list(x_data['x']) == ['x1'] * 4 + ['x2'] * 4 + ['x3'] * 2

    assert x_data.shape == (10, 4)
    assert xy_data.shape == (10, 5)
    assert z_data.shape == (6, 4)
    assert p_data.shape == (1, 2)
    assert m_data.shape == (1, 2)
    assert all_data.shape == (15, 8)
    assert no_data.empty is True


def test_datadict_arrange_for_multi_run(exp_results: ap.DataDict):

    results = exp_results
    data = _arrange_things(results)
    x_data, x_data2, xy_data, z_data, p_data, m_data, all_data, no_data = data

    assert x_data.equals(x_data2)
    assert x_data.shape == (40, 6)
    assert xy_data.shape == (40, 7)
    assert z_data.shape == (24, 6)
    assert p_data.shape == (2, 2)
    assert m_data.shape == (4, 3)
    assert all_data.shape == (60, 10)
    assert no_data.empty is True


def test_datadict_arrange_measures(exp_results: ap.DataDict):

    results = exp_results
    mvp_data = results.arrange(reporters=True, parameters=True)
    mvp_data_2 = results.arrange_reporters()
    assert mvp_data.equals(mvp_data_2)


def test_datadict_arrange_variables(exp_results: ap.DataDict):

    results = exp_results
    mvp_data = results.arrange(variables=True, parameters=True)
    mvp_data_2 = results.arrange_variables()
    assert mvp_data.equals(mvp_data_2)


def test_automatic_loading(model_results: ap.DataDict):

    if TEST_DIR in os.listdir():
        shutil.rmtree(TEST_DIR)

    results = model_results
    results.info['test'] = False
    results.save(exp_name="a", path=TEST_DIR)
    results.save(exp_name="b", exp_id=1, path=TEST_DIR)
    results.info['test'] = True
    results.save(exp_name="b", exp_id=3, path=TEST_DIR)
    results.info['test'] = False
    results.save(exp_name="c", path=TEST_DIR)
    results.save(exp_name="b", exp_id=2, path=TEST_DIR)

    loaded = ap.DataDict.load(path=TEST_DIR)
    shutil.rmtree(TEST_DIR)

    # Latest experiment is chosen (b),
    # and then highest id is chosen (3)

    assert loaded.info['test'] is True


def test_saved_equals_loaded(exp_results: ap.DataDict):

    results = exp_results
    results.save(path=TEST_DIR)
    loaded = ap.DataDict.load('ModelType0', path=TEST_DIR)
    shutil.rmtree(TEST_DIR)
    assert results == loaded
    # Test that equal doesn't hold if parts are changed
    assert results != 1
    loaded.reporters = 1
    assert results != loaded
    results.reporters = 1
    assert results == loaded
    loaded.info = 1
    assert results != loaded
    del loaded.info
    assert results != loaded


class WeirdObject:
    pass


def test_save_load():

    dd = ap.DataDict()
    dd['i1'] = 1
    dd['i2'] = np.int64(1)
    dd['f1'] = 1.
    dd['f2'] = np.float32(1.1)
    dd['s1'] = 'test'
    dd['s2'] = 'testtesttesttesttesttest'
    dd['l1'] = [1, 2, [3, 4]]
    dd['l2'] = np.array([1, 2, 3])
    dd['wo'] = WeirdObject()

    dd.save(path=TEST_DIR)
    dl = ap.DataDict.load(path=TEST_DIR)
    with pytest.raises(FileNotFoundError):
        assert ap.DataDict.load("Doesn't_exist", path=TEST_DIR)
    shutil.rmtree(TEST_DIR)
    with pytest.raises(FileNotFoundError):
        assert ap.DataDict.load("Doesn't_exist", path=TEST_DIR)

    assert dd.__repr__().count('\n') == 10
    assert dl.__repr__().count('\n') == 9
    assert len(dd) == 9
    assert len(dl) == 8
    assert dl.l1[2][1] == 4


def test_load_unreadable():
    """ Unreadable entries are loaded as None. """
    path = TEST_DIR / 'fake_experiment_1'
    os.makedirs(path)
    f = open(path / "unreadable_entry.xxx", "w+")
    f.close()
    dl = ap.DataDict.load(path=TEST_DIR)
    shutil.rmtree(TEST_DIR)
    assert dl.unreadable_entry is None

