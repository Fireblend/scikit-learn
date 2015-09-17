import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

class Modlem(BaseEstimator, ClassifierMixin):

    """Predicts the majority class of its training data."""

    def __init__(self):
        pass

    def fit(self, X, y):


        return self

    def predict(self, X):
        return np.repeat(self.classes_[self.majority_], len(X))

    def get_params(self, deep=True):
    # suppose this estimator has parameters "alpha" and "recursive"
        return {"alpha": self.alpha, "recursive": self.recursive}

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            self.setattr(parameter, value)
        return self
