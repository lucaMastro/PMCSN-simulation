import copy

class AccumSum:
                          # accumulated sums of                */
    service = None          #   service times                    */
    served = None           #   number served                    */

    def __init__(self):
        self.service = 0.0
        self.served = 0

    def copy(self):
        return copy.deepcopy(self)

    def __str__(self) -> str:
        return f'service: {self.service}; served: {self.served}'
        