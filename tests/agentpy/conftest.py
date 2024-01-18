from typing import Any

import pytest

import agentrs.agentpy as ap


class AgentType1(ap.Agent):
    def setup(self):
        self.x = 'x1'

    def action(self):
        self.record('x')


class AgentType2(AgentType1):
    def setup(self):
        self.x = 'x2'
        self.y = 'y2'

    def action(self):
        self.record(['x', 'y'])


class EnvType3(ap.Agent):
    def setup(self):
        self.x = 'x3'
        self.z = 'z4'

    def action(self):
        self.record(['x', 'z'])


class EnvType4(ap.Agent):
    def setup(self):
        self.z = 'z4'

    def action(self):
        self.record(['z'])


class ModelType0(ap.Model):

    def setup(self):
        self.E31 = EnvType3(self)
        self.E41 = EnvType4(self)
        self.E42 = EnvType4(self)
        self.agents1 = ap.AgentList(self, 2, AgentType1)
        self.agents2 = ap.AgentList(self, 2, AgentType2)
        self.agents = ap.AgentList(self, self.agents1 + self.agents2)
        self.envs = ap.AgentList(self, [self.E31, self.E41, self.E42])

    def step(self):
        self.agents.action()    # type: ignore
        self.envs.action()      # type: ignore

    def end(self):
        self.report('m_key', 'm_value')


@pytest.fixture()
def parameters() -> dict[str, Any]:
    return {
        'steps': 2,
        'px': ap.Values(1, 2),
        'report_seed': False,
    }

@pytest.fixture()
def sample(parameters: dict[str, Any]) -> ap.Sample:
    return ap.Sample(parameters)

@pytest.fixture()
def settings() -> dict[str, Any]:
    return {
        'iterations': 2,
        'record': True,
    }

@pytest.fixture()
def model_instance(sample: ap.Sample) -> ModelType0:
    return ModelType0(list(sample)[0])

@pytest.fixture()
def model_results(model_instance: ModelType0) -> ap.DataDict:
    return model_instance.run(display=False)

@pytest.fixture()
def exp_results(sample: ap.Sample, settings: dict[str, Any]) -> ap.DataDict:
    exp = ap.Experiment(ModelType0, sample, **settings)
    return exp.run(display=False)
