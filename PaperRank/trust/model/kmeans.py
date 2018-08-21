from sklearn.cluster import KMeans
import logging
import numpy as np


def computeKMeansProportions(data: np.array, n_clusters: int) -> np.array:
    """Function to compute cluster proportions for a given dataset and a
    given number of clusters.
    
    Arguments:
        data {np.array} -- Data to be clustered.
        n_clusters {int} -- Number of clusters.
    
    Returns:
        np.array -- Proportions of the data in each of the clusters.
    """

    # Reshaping data for K-Means Cluster
    X = data.reshape(-1, 1)

    logging.info('Computing K-Means for data of size {0} and {1} clusters'
                 .format(data.size, n_clusters))

    # Fitting K-Means model
    kmeans_model = KMeans(n_clusters=n_clusters, init='k-means++').fit(X=X)

    # Isolating labels
    kmeans_labels = kmeans_model.labels_

    logging.info('Computed K-Means clusters with {0} clusters'
                 .format(n_clusters))

    # Sorting cluster centers in ascending order
    cluster_ordered_idx = np.argsort(kmeans_model.cluster_centers_.reshape(-1))

    # Computing counts in each category (list needs to be reordered)
    unique, counts = np.unique(kmeans_labels, return_counts=True)

    # Sort counts in ascending order w.r.t. the cluster centers
    sorted_counts = np.array([counts[i] for i in cluster_ordered_idx])

    # Computing proportions in each of the clusters
    proportions = sorted_counts / np.sum(sorted_counts)

    return proportions
