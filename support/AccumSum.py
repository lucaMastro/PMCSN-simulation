import copy

class AccumSum:
                          # accumulated sums of                */
    service = None          #   service times                    */
    served = None           #   number served                    */

    def copy(self):
        return copy.deepcopy(self)
        