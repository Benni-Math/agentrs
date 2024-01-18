"""Types for Agentpy."""

from abc import abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any, Generic, Protocol, TypedDict, TypeVar

# Model protocol
TParameter = TypeVar('TParameter', bound=TypedDict, contravariant=True)
TOutput = TypeVar('TOutput', bound=Mapping, covariant=True)
class ModelProtocol(Protocol, Generic[TParameter, TOutput]):
    """Protocol defining what is required of a model."""
    p: Any
    _logs: Any
    t: int

    @abstractmethod
    def __init__(self, parameters: TParameter,
                 _run_id: Sequence[int] | None,
                 **kwargs: Any):
        """Initialize generically with TParameter."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Construct string representation, for output info."""
        pass


    # Handling object ids --------------------------------------------------- #

    @abstractmethod
    def _new_id(self) -> int:
        """Generate IDs for individual runs of the model."""
        pass


    # Recording ------------------------------------------------------------- #

    @abstractmethod
    def report(self, rep_keys: str | list[str], value: float | None) -> None:
        """Save selected info to the reporters."""
        pass


    # Placeholder methods for custom simulation methods --------------------- #

    @abstractmethod
    def setup(self, **kwargs) -> None:
        """
        Define the model's actions before the first simulation step.

        Can be overwritten to initiate agents and environments.
        """
        pass

    @abstractmethod
    def step(self) -> None:
        """
        Define the model's actions  during each simulation step (excluding `t==0`).

        Can be overwritten to define the models' main dynamics.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """
        Define the model's actions after each simulation step (including `t==0`).

        Can be overwritten for the recording of dynamic variables.
        """
        pass

    @abstractmethod
    def end(self) -> None:
        """
        Define the model's actions after the last simulation step.

        Can be overwritten for final calculations and reporting.
        """
        pass

    # Simulation routines (in line with ipysimulate) ------------------------ #

    @abstractmethod
    def set_parameters(self, parameters: TParameter) -> None:
        """Add and/or update the parameters of the model."""
        pass

    @abstractmethod
    def sim_setup(self, steps: int | None=None, seed: int | None=None) -> None:
        """Prepare time-step 0 of the simulation."""
        pass

    @abstractmethod
    def sim_step(self) -> None:
        """Single time step in a simulation."""
        pass

    @abstractmethod
    def sim_reset(self) -> None:
        """Reset model to initial conditions."""
        pass


    # Main simulation method for direct use --------------------------------- #

    @abstractmethod
    def stop(self) -> None:
        """Stop :meth:`Model.run` during an active simulation."""
        pass

    @abstractmethod
    def run(self, steps=None, seed=None, display=True) -> TOutput:
        """Execute the simulation of the model."""
        pass


    # Data management ------------------------------------------------------- #

    @abstractmethod
    def create_output(self) -> None:  # noqa: C901
        """Generate a `TOutput` object, which will be stored in :obj:`Model.output`."""
        pass

