from ..model import GammaMixModel

import numpy as np


def computeLogLikelihood(model: GammaMixModel, data: np.array,
                         posterior: np.ndarray) -> np.float:
    """Function to compute the log likelihood of a mixture model.
    
    Arguments:
        model {GammaMixModel} -- Model for which log likelihood is computed.
        data {np.array} -- Data computation is performed.
        posterior {np.ndarray} -- Posterior membership probabilities.
    
    Returns:
        np.float -- Log likelihood of the mixture model.
    """

    # Computing scaled PDF for each of the mixing Gamma distributions
    prob = model.computeScaledGammaPDF(data=data)

    # Computing log likelihood
    return np.sum(posterior * np.log(prob))
