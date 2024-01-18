from .object import Object

class SpatialEnvironment(Object):

    def record_positions(self, label='p'):
        """ Records the positions of each agent.

        Arguments:
            label (string, optional):
                Name under which to record each position (default p).
                A number will be added for each coordinate (e.g. p1, p2, ...).
        """
        for agent, pos in self.positions.items():
            for i, p in enumerate(pos):
                agent.record(label+str(i), p)
