import numpy as np

# import statsmodels.api as sm
from statsmodels.tsa.statespace.mlemodel import MLEModel


class BBTStateSpaceModel(MLEModel):
    def __init__(self, endog):
        # k_states=1 because we are modeling one latent state (e.g., cycle phase or temperature trend)
        super().__init__(endog=endog, k_states=1, initialization="diffuse")

        # Design matrix (Z): relates the state to the observation
        self.ssm["design"] = np.ones((1, 1))

        # Transition matrix (T): how the state evolves over time
        self.ssm["transition"] = np.ones((1, 1))

        # Selection matrix (R): relates the state error to the state equation
        self.ssm["selection"] = np.ones((1, 1))

        # Observed variance (H) and State variance (Q) will be estimated

    @property
    def param_names(self):
        return ["sigma2_obs", "sigma2_state"]

    @property
    def start_params(self):
        # Initial guesses for variances
        return [np.var(self.endog) * 0.5, np.var(self.endog) * 0.5]

    def transform_params(self, unconstrained):
        # Ensure variances are positive
        return np.asarray(unconstrained) ** 2

    def untransform_params(self, constrained):
        return np.asarray(constrained) ** 0.5

    def update(self, params, transformed=True, includes_fixed=False, complex_step=False):
        params = super().update(
            params,
            transformed=transformed,
            includes_fixed=includes_fixed,
            complex_step=complex_step,
        )

        # Observation variance
        self.ssm["obs_cov", 0, 0] = params[0]

        # State variance
        self.ssm["state_cov", 0, 0] = params[1]
