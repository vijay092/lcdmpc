import numpy as np
import autograd.numpy as np  # thinly-wrapped numpy
from numpy import dot as dot
from numpy import transpose as tp
from autograd import grad    # the only autograd function you may ever need

class sub_grid_aggregator:
    def __init__(self, horiz_len, num_downstream, num_upstream):
        self.gamma_scale = 1

        self.horiz_len = horiz_len
        self.num_downstream = num_downstream
        self.num_upstream = num_upstream
        self.num_bldgs_downstream = num_downstream - 1

        inputs = np.array([0.0])
        disturbances = np.array([0.0])
        self.reinit(inputs, disturbances)

        # self.Z_idn = [i + 1 for i in range(self.num_downstream)]
        # print('here: ', self.Z_idn)
        # lkj

    def reinit(self, inputs, disturbances):
        # inputs

        # disturbances
        # self.disturbances = disturbances

        # Model matrices
        # print(self.num_downstream)
        # lkj
        self.A = np.zeros((1, 1))
        self.Bu = np.zeros((1, self.num_bldgs_downstream))
        self.Bv = np.zeros((1, self.num_upstream))
        self.Bd = np.zeros((1, 1)) 

        self.Bu_mean_inputs = np.zeros((1, self.num_bldgs_downstream))
        self.Bd_mean_inputs = np.array([0.0])
        self.Cy_mean_outputs = np.zeros((self.num_downstream, 1))
        self.Cz_mean_outputs = np.zeros((self.num_downstream, 1))

        self.Cy = np.array(
            [[0.0] for i in range(self.num_downstream)]
        )
        self.Dyu = np.array(
            np.vstack(
                [
                    [-1.0]*self.num_bldgs_downstream, # total p_ref power for tracking p_ref from super grid agg
                    -1.0*np.eye(self.num_bldgs_downstream) # ref to send to buildings
                ]
            )
        )
        # print(np.shape(self.Dyu))
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!', self.Dyu)
        # print('num downstream: ', self.num_downstream)
        # lkj

        # self.Dyv = np.array(
        #     np.vstack(
        #         [
        #             [1.0], # power ref from super grid agg
        #             [np.eye(self.num_downstream)] # building powers
        #         ]
        #     )
        # )
        self.Dyv = np.array(
            np.eye(self.num_upstream)
        )
        # print(np.shape(self.Dyv))
        # print(self.Dyv)
        # lkj
        self.Dyd = np.zeros((self.num_downstream, 1))
        # print(self.Dyd)
        # lkj

        self.Cz = np.zeros((self.num_downstream, 1))
        # self.Dzu = np.eye(self.num_downstream, 2) # total p_ref power to send to super grid agg
        # self.Dzu = np.array([[1., 1., 1.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        # self.Dzu = np.array([[1., 1.], [1., 0.], [0., 1.]])
        Dzu0 = np.array([1.]*self.num_bldgs_downstream)
        self.Dzu = np.vstack((Dzu0, np.eye(self.num_bldgs_downstream)))
        self.Dzv = np.zeros((self.num_downstream, self.num_upstream))
        self.Dzd = np.zeros((self.num_downstream, 1))

        self.Cy_lin = np.zeros((self.num_downstream, 1))
        self.Cz_lin = np.zeros((self.num_downstream, 1))

        self.Dyu_lin = np.zeros((self.num_downstream, 1))
        self.Dzu_lin = np.zeros((self.num_downstream, 1))

        self.Dyd_lin = np.zeros((self.num_downstream, 1))
        self.Dzd_lin = np.zeros((self.num_downstream, 1))

    def process_Q(self, Q):
        # print(Q)
        # lkj
        Q = np.zeros(np.shape(Q))
        # Q[0, 0] = 1.0
        # Q[1, 1] = 5.0*1e-7
        # Q[2, 2] = 5.0*1e-7
        # Q[3, 3] = 5.0*1e-7
        # Q[4, 4] = 1.0
        # Q[5, 5] = 5.0*1e-7
        # Q[6, 6] = 5.0*1e-7
        # Q[7, 7] = 5.0*1e-7
        for i in range(self.horiz_len):
            Q[i*self.num_downstream, i*self.num_downstream] = 1.0
            for j in range(self.num_bldgs_downstream):
                Q[i*self.num_downstream + (j + 1), i*self.num_downstream + (j + 1)] = 5.0*1e-7
        # Q[4, 4] = 1.0*1e-10
        # Q[5, 5] = 1.0*1e-10
        # print(Q)
        # lkj
        # for i in range(self.num_downstream):
        #     for j in np.arange(i+1, len(Q), (self.num_downstream + 1)):
        #         Q[j] = np.zeros(len(Q))
        # for i in np.arange(1, len(Q), 4):
        #     Q[i] = np.zeros(len(Q))
        # for i in np.arange(2, len(Q), 4):
        #     Q[i] = np.zeros(len(Q))
        # for i in np.arange(3, len(Q), 4):
        #     Q[i] = np.zeros(len(Q))
        # print('#########: ', Q)
        # lkj
        return Q*1.0e2

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
        # print('grid bldg refs: ', self.bldg_Prefs)
        return self.bldg_Prefs

    def add_var_group(self, optProb):
        optProb.addVarGroup(
            'bldg_Prefs', self.horiz_len*(self.num_downstream - 1), type='c',
            lower=0.0, upper=500.0, value=50.0
        )
        self.numDVs = self.num_downstream - 1
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
            # print('*** 1: ', np.array(refs).reshape(len(refs), 1))
            return np.array(refs).reshape(len(refs), 1)
        else:
            # print('*** 2: ', np.array(refs).reshape(len(refs), 1))
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
