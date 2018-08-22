from .data_management import shiftData, computeLocation
from ..model import GammaMixModel

from scipy.stats import dirichlet
import numpy as np


def initializeGammaModelEM(data: np.array, m: int,
                           weights_init: np.array=None) -> GammaMixModel:
    """Function to initialize a GammaMixModel for the Expectation Maximization
    algorithm. Initialization weights can be provided, but if not a Dirichlet
    Process prior is used to estimate initial weights. The data is then sorted
    and partitioned to compute parameter estimates for each of the mixture
    distributions, using formulas from http://bit.ly/2OUItXY. This function
    intelligently scales the data if necessary, and computes the relevant
    location parameter for the mixture distributions.
    
    Arguments:
        data {np.array} -- Original data.
        m {int} -- Number of mixing distributions.
    
    Keyword Arguments:
        weights_init {np.array} -- Initial weights (default: {None}).
    
    Returns:
        GammaMixModel -- GammaMixModel object initialized with intelligent
                         parameter estimates for each of the
                         mixture distributions.
    """

    if weights_init is None:
        # Estimating initial weights from a Dirichlet Process
        weights_init = dirichlet.rvs(alpha=np.ones(m), size=1)[0]
        # Sort weights (to model [expected] exponential decay of data)
        # Note: This is specific to PaperRank; dependent on data assumptions
        weights_init = np.sort(weights_init)[::-1]
    
    # Checking if the data is negative; if so, shift
    data_shifted = shiftData(data=data) if np.any(data[data <= 0]) else data

    # Sorting data
    data_sorted = np.sort(data_shifted)

    # Initializing empty parameters matrix, with shape (m x 2)
    params_init = np.ones(m * 2).reshape(-1, 2)

    # Computing intervals for the parameter estimation
    intervals = np.cumsum(np.append(0, weights_init))

    for i in range(1, intervals.size):
        # Computing upper and lower bounds for the interval
        lower_bound = int(data.size * intervals[i - 1])
        upper_bound = int(data.size * intervals[i])

        # Isolating interval
        data_subset = np.array(data_sorter[lower_bound:upper_bound])

        # NOTE: For more information on the equations used to compute estimates
        #       for the Gamma Distributions, see: http://bit.ly/2OUItXY
        
        # Computing s
        n = data_subset.size
        s = np.log(1 / n * np.sum(data_subset)) \
            - (1 / n * np.sum(np.log(data_subset)))

        # Computing estimates for shape $k$ and scale $\theta$
        k = (3 - s + np.sqrt((s - 3)**2 + (24 * s))) / (12 * s)
        theta = 1 / (k * n) * np.sum(data_subset)

        # Adding to params matrix
        params_init[(i - 1)][0] = k
        params_init[(i - 1)][1] = theta
    
    # Computing location
    loc_init = computeLocation(data=data, data_shifted=data_shifted)

    # Create new GammaMixModel object, return
    return GammaMixModel(weights=weights_init,
                         params=params_init,
                         loc=loc_init,
                         m=m)
