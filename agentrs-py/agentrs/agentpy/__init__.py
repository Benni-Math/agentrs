"""
Agentpy - Agent-based modeling in Python
Copyright (c) 2020-2021 Joël Foramitti

Documentation: https://agentpy.readthedocs.io/
Examples: https://agentpy.readthedocs.io/en/latest/model_library.html
Source: https://github.com/JoelForamitti/agentpy

Modified by Benedikt Arnarsson for use in dentalcaries project.
"""

__all__ = [
    # '__version__',
    'Model',
    'Agent',
    # 'AgentList', 'AgentDList', 'AgentSet',
    'AgentList', 'AgentSet',
    # 'AgentIter', 'AgentDListIter', 'AttrIter',
    'AgentIter', 'AttrIter',
    'Grid', 'GridIter',
    'Space',
    'Network', 'AgentNode',
    'Experiment',
    'DataDict',
    'Sample', 'Values', 'Range', 'IntRange',
    'gridplot', 'animate',
    'AttrDict'
]

from .agent import Agent
from .datadict import DataDict
from .experiment import Experiment
from .grid import Grid, GridIter
from .model import Model
from .network import Network, AgentNode
from .sample import IntRange, Range, Sample, Values
from .sequences import (
    AgentIter,
    AgentList,
    AgentSet,
    AttrIter,
)
from .space import Space
from .tools import AttrDict
from .visualization import gridplot, animate
