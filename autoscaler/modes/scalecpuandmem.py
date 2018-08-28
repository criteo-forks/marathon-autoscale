import operator
import sys

from autoscaler.modes.abstractmode import AbstractMode
from autoscaler.modes.scalecpu import ScaleByCPU
from autoscaler.modes.scalemem import ScaleByMemory


class ScaleByCPUAndMemory(AbstractMode):

    def __init__(self,  api_client=None, app=None, dimension=None):
        super().__init__(api_client, app)
        self.dimension = dimension
        self.mode_map = {'cpu': ScaleByCPU, 'mem': ScaleByMemory}

        if len(dimension['min']) < 2 or len(dimension['max']) < 2:
            self.log.error("Scale mode AND requires two comma-delimited "
                           "values for MIN_RANGE and MAX_RANGE.")
            sys.exit(1)

        # Instantiate the CPU/Memory mode classes
        for idx, mode in enumerate(list(self.mode_map.keys())):
            self.mode_map[mode] = self.mode_map[mode](
                api_client,
                app,
                dimension={
                    'min': dimension['min'][idx],
                    'max': dimension['max'][idx]
                }
            )

    def scale_direction(self):
        """
        Performs a bitwise AND on the returned direction for CPU (x)
        and Memory (y). Take the absolute value of the direction, then
        perform the bitwise AND calculation. If (x = y = 1), return 1,
        otherwise return 0. Sign will be flipped based on scale direction.
        """
        results = []
        negative = False

        for mode in list(self.mode_map.keys()):
            d = self.mode_map[mode].scale_direction()
            if d < 0:
                negative = True
                d = abs(d)
            results.append(d)

        for mode in list(self.mode_map.keys()):
            results.append(self.mode_map[mode].scale_direction())

        if results[0] == results[1]:
            return results[0]
        else:
            return 0

            if d < 0:
                negative = True
                d = abs(d)
            results.append(d)

        # perform bitwise AND operation on values
        result = operator.and_(results[0], results[1])

        return result if not negative else -result
