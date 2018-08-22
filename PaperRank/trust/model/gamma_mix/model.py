from scipy.stats import gamma
import numpy as np


class GammaMixModel():
    """GammaMixModel encapsulates the parameterization of a Gamma Mixture Model,
    with all necessary attributes. It also contains functionality to compute
    posterior membership probabilities using the mixture model.
    """

    def __init__(self, weights: np.array, params: np.ndarray, loc: float):
        """Gamma Mixture Model initialization.
        
        Arguments:
            weights {np.array} -- Weights (i.e. mixture proportions) of the
                                  Gamma mixtures.
            params {np.array} -- Parameters of each of the mixture Gamma
                                 distributions (m x 2; m = number of mixtures).
            loc {float} -- Location parameter for the mixture distributions.
        """

        # Save each of the parameters
        self.weights = weights
        self.params = params
        self.loc = loc

    def computeMembership(self, data: np.array, params_new: np.ndarray=None,
                          update_weights: bool=False) -> np.ndarray:
        """Function to compute posterior membership probabilities given some
        data. This is computed by calculating the PDF of the data for each
        of the mixing Gamma distributions, and dividing by the sum of them to
        coerce these values into a probability distribution.
        That is, if the vector of Gamma distribution probabilities for a data
        point is A, then the posterior probability is A/sum(A).
        
        Arguments:
            data {np.array} -- Data computation is performed on.
        
        Keyword Arguments:
            params_new {np.ndarray} -- Optional set of parameters to be used to 
                                       calculate the posterior membership
                                       probabilities (default: {None}).
            update_weights {bool} -- True to update existing
                                     weights (default: {False}).
        
        Returns:
            np.ndarray -- Posterior membership probabilities for the data.
        """

        # Update model parameters if not none
        if params_new is not None:
            self.params = params_new

        # Computing Gamma distribution probabilities for each distribution
        scaled_gamma_pdf = self.__computeScaledGammaPDF(data=data)

        # Computing posterior membership probabilities
        # Note: axis=0 indicates column-wise sum
        posterior = scaled_gamma_pdf / np.sum(scaled_gamma_pdf, axis=0)

        # Check if weights are to be updated
        if update_weights:
            self.__updateWeights(posterior=posterior)

        return posterior

    def __computeScaledGammaPDF(self, data: np.array) -> np.ndarray:
        """Function to compute the scaled Gamma distribution PDFs for each of
        the mixture distributions, for a given set of data. The scaled PDF is
        computed by multiplying the PDF of the Gamma distribution by the weight
        of the mixture distribution.
        
        Arguments:
            data {np.array} -- Data computation is performed on.
        
        Returns:
            np.ndarray -- Scaled Gamma Distribution PDFs for each of the
                          mixture distributions.
        """

        # Compute probabilities for each of the distributions
        probs = [self.weights[i] * gamma.pdf(x=data,
                                             shape=self.params[i][0],
                                             scale=self.params[i][1],
                                             loc=self.loc)
                 for i in range(self.weights.size)]

        # Cast to np.ndarray, return
        return np.array(probs)
    
    def __updateWeights(self, posterior: np.ndarray):
        """Function to update the weights of the mixture distributions,
        given a set of posterior probabilities. The weights are set to
        the mean of the posterior probabilities with respect to each mixing
        distribution.
        
        Arguments:
            posterior {np.ndarray} -- Poseterior membership probabilities.
        """

        # Note: axis=1 indicates row-wise mean
        self.weights = np.mean(posterior, axis=1)
