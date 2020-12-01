import numpy as np
import autograd.numpy as np  # thinly-wrapped numpy
from numpy import dot as dot
from numpy import transpose as tp
from autograd import grad    # the only autograd function you may ever need

class grid_aggregator:
    def __init__(self, horiz_len, num_downstream):
        self.gamma_scale = 1

        self.horiz_len = horiz_len
        self.num_downstream = num_downstream

        inputs = np.array([0.0])
        disturbances = np.array([0.0])
        self.reinit(inputs, disturbances)

        self.Z_idn = [i + 1 for i in range(self.num_downstream)]

    def reinit(self, inputs, disturbances):
        # inputs

        # disturbances
        # self.disturbances = disturbances

        # Model matrices
        self.A = np.zeros((self.num_downstream, self.num_downstream))
        self.Bu = np.zeros((self.num_downstream, self.num_downstream))
        self.Bv = np.zeros((self.num_downstream, self.num_downstream))
        self.Bd = np.zeros((self.num_downstream, 1)) 

        self.Bu_mean_inputs = np.zeros((self.num_downstream, self.num_downstream))
        self.Bd_mean_inputs = np.array([0.0])
        self.Cy_mean_outputs = np.zeros((self.num_downstream + 1, 1))
        self.Cz_mean_outputs = np.zeros((self.num_downstream, 1))

        self.Cy = np.array(
            [[0.0]*self.num_downstream for i in range(self.num_downstream + 1)]
        )
        self.Dyu = np.array(
            np.vstack(
                [
                    [1.0]*self.num_downstream,
                    -1.0*np.eye(self.num_downstream)
                ]
            )
        )
        self.Dyv = np.array(
            np.vstack(
                [
                    [0.0]*self.num_downstream,
                    np.eye(self.num_downstream)
                ]
            )
        )
        self.Dyd = np.zeros((self.num_downstream+1, 1))

        self.Cz = np.zeros((self.num_downstream, self.num_downstream))
        self.Dzu = np.eye(self.num_downstream)
        self.Dzv = np.zeros((self.num_downstream, self.num_downstream))
        self.Dzd = np.zeros((self.num_downstream, 1))

        self.Cy_lin = np.zeros((self.num_downstream+1, 1))
        self.Cz_lin = np.zeros((self.num_downstream, 1))

        self.Dyu_lin = np.zeros((self.num_downstream+1, 1))
        self.Dzu_lin = np.zeros((self.num_downstream, 1))

        self.Dyd_lin = np.zeros((self.num_downstream+1, 1))
        self.Dzd_lin = np.zeros((self.num_downstream, 1))

    def process_Q(self, Q):
        return Q*1.0e-5

    def process_S(self, S):
        S = S
        return S

    def get_forecast(self, current_time, disturbance_data):
        return np.array([[0.0]])

    def parse_opt_vars(self, varDict):
        self.bldg_Prefs = varDict['bldg_Prefs']
        self.bldg_Prefs = np.array(self.bldg_Prefs).reshape(
            np.shape(self.bldg_Prefs)[0],1
        )
        return self.bldg_Prefs

    def parse_sol_vars(self, sol):
        self.bldg_Prefs = list(sol.getDVs().values())[0]
        self.bldg_Prefs = np.array(self.bldg_Prefs).reshape(
            np.shape(self.bldg_Prefs)[0], 1
        )
        return self.bldg_Prefs

    def add_var_group(self, optProb):
        optProb.addVarGroup(
            'bldg_Prefs', self.horiz_len*self.num_upstream, type='c',
            lower=0.0, upper=100.0, value=5.0
        )
        self.numDVs = self.num_downstream
        return optProb

    def add_con_group(self, optProb):
        return optProb

    def compute_cons(self, funcs, uOpt, Y):
        return funcs

    def update_inputs(self, states, control_actions, outputs):
        return np.array([0.0])

    def update_disturbances(self, d):
        self.d = np.array([0.0])

    def process_refs(self, refs):
        return refs

    def process_refs_horiz(self, refs=None, refs_const=None, refs_total=None, current_time=None):
        if refs_total is not None:
            refs_start = np.where(refs_total['time'] == current_time)[0][0]
            refs = refs_total['grid_ref'][refs_start: refs_start + self.horiz_len]
            refs = np.array([val for val in refs]).flatten()
            return np.array(refs).reshape(len(refs), 1)
        else:
            return np.array(refs).reshape(len(refs_const), 1)

    def sensitivity_func(self):
        return 0.0

    def process_uConv(self, uConv):
        return np.array(uConv).reshape(np.shape(uConv)[0], 1)

    def simulate(self, current_time, inputs, disturb, v):
        self.outputs = inputs
        return inputs

    def filter_update(self, states, outputs):
        return states