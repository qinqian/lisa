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
    def __init__(self, reg_log2, gene_binary, jobs=5, covariates=True):
        """
        reg_log2: StandardScaler log2 regulatory potential pd.DataFrame
        """
        self.reg_log2 = reg_log2
        self.gene_binary = gene_binary
        self.jobs = jobs
        self.covariates = None
        if covariates:
            self.covariates = self.reg_log2.loc[:, 'GC']
            self.reg_log2 = self.reg_log2.drop('GC', axis=1, inplace=False)

    def select_feature(self, n_samp=10, low=0, epsilon=1e-6):
        """ select parameters with binary search of lambda
        to get an arbitrary n_samp samples
        """
        # self._select_k_feature(200)
        penalty = np.arange(1e-6, 0.1, 1e-6)
        high = len(penalty)-1
        while low <= high:
            mid = (low + high) // 2
            model = _get_model(penalty[mid])
            model.fit(self.reg_log2, self.gene_binary)
            sel = np.abs(model.coef_[0]) >= epsilon
            snum = np.sum(sel)
            if snum >= n_samp+2:
                # too many samples, prefer stronger regularization, lower C
                high = mid - 1
            elif snum <= n_samp-2:
                low = mid + 1
            else:
                break
        print('feature ready...', snum)
        self.reg_log2 = self.reg_log2.ix[:, sel]

    def _select_k_feature(self, n_samp=200):
        """ anova feature select a fixed number of n_samp samples """
        if self.reg_log2.shape[1] <= n_samp:
            n_samp = self.reg_log2.shape[1] - 1
        select = SelectKBest(f_classif, k=n_samp)
        select.fit(self.reg_log2, self.gene_binary)
        self.reg_log2 = self.reg_log2.ix[:, select.get_support()]

    def _select_feature2(self):
        """ cross validation with random search to select a certain amount of
        samples based on the best average validation auc score """
        self._select_k_feature(200)
        lisa_expression_rs = RandomizedSearchCV(Pipeline([('clf', _get_model())]),
                                                {'clf__C': uniform(loc=0.001, scale=0.2)},
                                                n_jobs=self.jobs, n_iter=10, cv=self.jobs,
                                                scoring=make_scorer(roc_auc_score),
                                                random_state=999)
        lisa_expression_rs.fit(self.reg_log2, self.gene_binary)
        best_params, coefs, prauc, auc = self.evaluate(lisa_expression_rs)
        select = np.abs(coefs) >= 1e-6
        self.reg_log2 = self.reg_log2.ix[:, select]
        print(best_params, coefs, prauc, auc)

    def _select_feature3(self):
        """ use few genes with all samples to do the cross validation for searching
        lambda to get the optimal sample set """
        np.random.RandomState(999)

        diff_index, = np.where(self.gene_binary==1)
        diff_response = self.gene_binary[diff_index]

        diff_reg_df = self.reg_log2.ix[diff_index, :]
        diff_reg_median = diff_reg_df.median(axis=1) # gene regulatory potential median

        non_diff_index, = np.where(self.gene_binary==0)
        non_diff_reg_df = self.reg_log2.ix[non_diff_index, :]
        non_diff_reg_median = non_diff_reg_df.median(axis=1) # gene regulatory potential median

        # non and DE gene has the same sample median range
        same_range_nondiff_index, = np.where((non_diff_reg_median <= diff_reg_median.max()) & \
                                             (non_diff_reg_median >= diff_reg_median.min()))
        same_range_nondiff_rindex = np.random.choice(same_range_nondiff_index, len(diff_index) * 3, replace=False)

        non_diff_response = self.gene_binary[non_diff_index][same_range_nondiff_rindex]

        non_diff_reg_df = non_diff_reg_df.ix[same_range_nondiff_rindex, :]

        reg_log2_subset = pd.concat([diff_reg_df,
                                     non_diff_reg_df],
                                    axis=0)
        response = np.concatenate([diff_response, non_diff_response])

        print(reg_log2_subset.shape)
        lisa_expression_rs = RandomizedSearchCV(Pipeline([('clf', _get_model())]),
                                                {'clf__C': uniform(loc=1e-2, scale=0.5)},
                                                n_jobs=self.jobs, n_iter=30, cv=self.jobs,
                                                scoring=make_scorer(roc_auc_score),
                                                random_state=999)
        lisa_expression_rs.fit(reg_log2_subset, response)

        best_params, coefs, prauc, auc = self.evaluate(lisa_expression_rs)
        select = np.abs(coefs) >= 1e-6
        self.reg_log2 = self.reg_log2.ix[:, select]

    def evaluate(self, model):
        """evaluate the model performance
        and extract coefficientts
        """
        prediction = model.predict_log_proba(self.reg_log2)[:, 1]
        prauc = average_precision_score(self.gene_binary, prediction)
        auc = roc_auc_score(self.gene_binary, prediction)
        coefs = model.best_estimator_.named_steps['clf'].coef_[0]
        best_params = model.best_params_.get('clf__C', None)
        return best_params, coefs, prauc, auc

    def train(self):
        """
        reg_potential: regulatory potential of a epigenome type (X)
        gene_binary:   binary vector for differential genes     (Y)
        jobs: threads when cross validation
        """
        self.select_feature(10)   # original feature selection with binary search lambda
        # self._select_feature2()   # anova 200~300 samples with cross validation of lambda search
        # self._select_feature3()

        print(self.reg_log2.shape)
        # add back covariates
        if isinstance(self.covariates, pd.Series):
            self.reg_log2 = pd.concat([self.reg_log2, self.covariates], axis=1)

        # cross validation with grid search
        fold = KFold(n_splits=self.jobs, shuffle=True, random_state=777)
        np.random.RandomState(777)
        parameters = {'clf__C': np.random.uniform(1e5, 1e8, 3)}
        lisa_expression_gs = GridSearchCV(Pipeline([('clf', _get_model(regularized='l2'))]),
                                          parameters, n_jobs=self.jobs, cv=fold,
                                          scoring=make_scorer(roc_auc_score))
        lisa_expression_gs.fit(self.reg_log2, self.gene_binary)
        best_params, coefs, prauc, auc = self.evaluate(lisa_expression_gs)
        coefs = pd.DataFrame(coefs, index=self.reg_log2.columns, columns=["coefficients"])
        coefs = coefs[np.abs(coefs.values) >= 1e-6]
        coefs = coefs.iloc[np.argsort(np.abs(coefs.iloc[:, 0]))[::-1], :]
        print(best_params)
        return auc, prauc, coefs
