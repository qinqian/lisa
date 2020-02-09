""" build logistic regression with l1 penalty,
X: regulatory potential, Y: differential expression gene set
"""
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, average_precision_score, roc_auc_score
from sklearn.feature_selection import SelectKBest, f_classif

import numpy as np
import pandas as pd
from scipy.stats import uniform

def _get_model(penalty=1, regularized='l1'):
    """ generate sklearn model instance with parameter
    """
    return LogisticRegression(penalty=regularized, tol=0.01, dual=False,
                              C=penalty, random_state=999)

class Logit(object):
    """ logistic regression class
    """
    def __init__(self, reg_log2, gene_binary, covariates=True):
        """
        reg_log2: StandardScaler log2 regulatory potential pd.DataFrame
        """
        self.reg_log2 = reg_log2
        self.gene_binary = gene_binary
        self.covariates = None
        if covariates:
            self.covariates = self.reg_log2.loc[:, 'GC']
            self.reg_log2 = self.reg_log2.drop('GC', axis=1, inplace=False)

    def select_feature(self, n_samp=10, low=0, epsilon=1e-6):
        """ select parameters with binary search of lambda
        to get an arbitrary n_samp samples
        """
        self._select_k_feature(200)
        penalty = np.arange(1e-8, 1, 1e-8)
        high = len(penalty)-1
        while low <= high:
            mid = (low + high) // 2
            model = _get_model(penalty[mid])
            model.fit(self.reg_log2, self.gene_binary)
            sel = np.abs(model.coef_[0]) >= epsilon
            snum = np.sum(sel)
            if snum >= n_samp+1:
                # too many samples, prefer stronger regularization, lower C
                high = mid - 1
            elif snum <= n_samp-1:
                low = mid + 1
            else:
                break
        #print('feature ready...', snum)
        self.reg_log2 = self.reg_log2.loc[:, sel]

    def _select_k_feature(self, n_samp=200):
        """ anova feature select a fixed number of n_samp samples """
        if self.reg_log2.shape[1] <= n_samp:
            n_samp = self.reg_log2.shape[1] - 1
        select = SelectKBest(f_classif, k=n_samp)
        select.fit(self.reg_log2, self.gene_binary)
        self.reg_log2 = self.reg_log2.loc[:, select.get_support()]

    def _select_feature2(self, upper_bound=0.5):
        """ cross validation with random search to select a certain amount of
        samples based on the best average validation auc score

        combine anova, random search and binary search together
        """
        lisa_expression_rs = RandomizedSearchCV(Pipeline([('clf', _get_model())]),
                                                {'clf__C': uniform(loc=1e-3,
                                                                   scale=upper_bound)},
                                                n_iter=10, cv=3, n_jobs=1,
                                                scoring=make_scorer(roc_auc_score),
                                                random_state=999)
        lisa_expression_rs.fit(self.reg_log2, self.gene_binary)
        best_params, coefs, prauc, auc = self.evaluate(lisa_expression_rs)
        select = np.abs(coefs) >= 1e-6
        self.reg_log2 = self.reg_log2.loc[:, select]
        #print(best_params, coefs, prauc, auc)
        #print(self.reg_log2.shape)
        if np.sum(select) >= 10:
            self._select_feature2(upper_bound/1.5)

    def evaluate(self, model):
        """evaluate the model performance
        and extract coefficients
        """
        prediction = model.predict_log_proba(self.reg_log2)[:, 1]
        prauc = average_precision_score(self.gene_binary, prediction)
        auc = roc_auc_score(self.gene_binary, prediction)
        coefs = model.best_estimator_.named_steps['clf'].coef_[0]
        best_params = model.best_params_.get('clf__C', None)
        return best_params, coefs, prauc, auc

    def train(self, sample_number):
        """
        reg_potential: regulatory potential of a epigenome type (X)
        gene_binary:   binary vector for differential genes     (Y)
        jobs: threads when cross validation
        """
        self.select_feature(sample_number)   # original feature selection with binary search lambda
        # self._select_feature2()     # anova 200~300 samples with cross validation of lambda search
        # add back covariates
        if isinstance(self.covariates, pd.Series):
            self.reg_log2 = pd.concat([self.reg_log2, self.covariates], axis=1)

        # cross validation with grid search
        fold = KFold(n_splits=3, shuffle=True, random_state=777)
        np.random.RandomState(777)
        parameters = {'clf__C': np.random.uniform(1e-2, 1e5, 5)}
        lisa_expression_gs = GridSearchCV(Pipeline([('clf', _get_model(regularized='l1'))]),
                                          parameters, cv=fold, n_jobs=1,
                                          scoring=make_scorer(roc_auc_score))
        lisa_expression_gs.fit(self.reg_log2, self.gene_binary)
        best_params, coefs, prauc, auc = self.evaluate(lisa_expression_gs)
        coefs = pd.DataFrame(coefs, index=self.reg_log2.columns, columns=["coefficients"])
        coefs = coefs[np.abs(coefs.values) >= 1e-6]
        coefs = coefs.iloc[np.argsort(np.abs(coefs.iloc[:, 0]))[::-1], :]
        #print(best_params)
        return auc, prauc, coefs
