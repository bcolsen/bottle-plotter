from __future__ import division, print_function
"""
Implementation of Peirce's Criterion for Outlier Rejection.

This module provides the `PeirceCriteria` class, which implements Peirce's
Criterion, a statistical method for identifying and rejecting outliers from a
dataset. The criterion is based on the probability of observing errors of a
certain magnitude and aims to find a threshold (R-value) to distinguish
outliers from valid data points.

The method iteratively determines the R-value and checks for data points
exceeding this threshold relative to the standard deviation. The process
continues until no more outliers are identified or a limit is reached.

References:
- Peirce, B. (1852). Criterion for the rejection of doubtful observations.
  The Astronomical Journal, 2, 161-163.
- Ross, S. L. (2003). Peirce's Criterion for the Rejection of Outliers.
  Journal of Engineering Technology, 20(2), 38-41.
"""
import numpy as np
import pylab as plt
import scipy.special as sp
import math

class PeirceCriteria:
    """
    Applies Peirce's Criterion to identify and reject outliers in a dataset.

    Peirce's Criterion is an iterative statistical method used to find data
    points that are unlikely to belong to the dataset given a certain number
    of observations and unknown quantities.

    The original simple docstring for this class (which is replaced by this one) was:
    ''' use Peirce's Criterion to reject outlier data point from a dataset
        x - dataset to be evaluated (1xN vector)
        m - number of unknown quantities'''

    Attributes
    ----------
    x2 : numpy.ndarray
        The dataset after removing the identified outliers. If no outliers
        are found or if an error occurs (e.g., `PeirceBisect` fails to find R),
        this will be the original dataset passed to `__init__`.
    RejVec : numpy.ndarray of bool
        A boolean array of the same length as the original input data `x`,
        where `True` indicates that the corresponding data point was rejected
        as an outlier.
    AcceptVec : numpy.ndarray of bool
        A boolean array of the same length as the original input data `x`,
        where `True` indicates that the corresponding data point was accepted
        (i.e., not an outlier).
    """
    def __init__(self, x_input, m_unknown):
        # In the original code, parameters are (x, m). Using (x_input, m_unknown) in this docstring for clarity.
        """
        Initialize and apply Peirce's Criterion to the dataset.

        The process involves:
        1. Calculating the mean and standard deviation (with `ddof=1`) of the
           input dataset `x_input`.
        2. Iteratively attempting to identify outliers:
           a. Start by suspecting `n_suspect = 1` outlier.
           b. Calculate the Peirce threshold `R` using `self.PeirceBisect` for
              the total number of observations `N_obs`, current `n_suspect`,
              and number of unknown quantities `m_unknown`.
           c. If `R` cannot be determined (e.g., `PeirceBisect` returns `None`),
              the process stops. The existing `print` statements in the code
              will indicate failures or progress.
           d. Determine the number of data points (`current_rejected_count`) whose
              absolute deviation from the mean (scaled by sigma) exceeds `R`.
           e. If `current_rejected_count` is greater than `prev_rejected_count`
              (number of outliers confirmed in the previous iteration), then these
              `current_rejected_count` points are considered the new set of
              potential outliers. `self.RejVec`, `self.AcceptVec`, and `self.x2`
              are updated. `prev_rejected_count` is updated to
              `current_rejected_count`. `n_suspect` is incremented by 1 for
              the next iteration (as per original code's `n += 1` logic).
           f. If `current_rejected_count` is not greater than `prev_rejected_count`,
              it means that attempting to identify `n_suspect` outliers did not lead
              to finding *more* outliers than previously confirmed. The process stops,
              and the outliers confirmed in the *previous* iteration (if any)
              are considered final.
           g. The loop also stops if `n_suspect` grows to be more than half of `N_obs`.
        3. The attributes `x2`, `RejVec`, `AcceptVec` store the result of this
           iterative process. If no outliers are ever confirmed, `x2` is the
           original dataset, `RejVec` is all `False`, and `AcceptVec` is all `True`.

        Parameters
        ----------
        x_input : array_like
            The input dataset (1D array or list of numerical values).
            Corresponds to `x` in the method signature.
        m_unknown : int
            The number of unknown quantities in the underlying model from which
            the data `x_input` is derived. For example, if only the mean is
            considered unknown, `m_unknown=1`. If both mean and standard
            deviation are estimated from the sample, `m_unknown=2` is often used.
            Corresponds to `m` in the method signature.
        """
        # calculate mean and standard deviation
        x_data = np.array(x_input) # Parameter name in code is x
        
        xbar = np.mean(x_data)
        sigma = np.std(x_data, ddof=1) # Use sample standard deviation

        # Number of measurements
        N_obs = len(x_data) # Parameter name in code for N_obs is N

        # residuals
        delta = abs(x_data-xbar)

        # Number of rejected measurements confirmed in the *previous* iteration.
        # Original name: Rej1
        prev_rejected_count = 0

        # n_suspect is the number of data points *currently suspected* to be outliers,
        # for which an R-value is being calculated. Starts at 1.
        # Original name: n
        n_suspect = 1 
        
        # Initialize attributes to default (no outliers found yet).
        # These will be updated if outliers are identified and confirmed by the loop.
        self.x2 = x_data # Default to original data
        self.RejVec = np.zeros(N_obs, dtype=bool) # Default to no rejections
        self.AcceptVec = np.ones(N_obs, dtype=bool) # Default to all accepted

        while(1):
            # Debug print from original code (parameters were x, delta, sigma, m):
            # print( x_data, delta, sigma, m_unknown, ) # Using new var names for clarity
            
            # Condition to stop: if suspecting more than half the dataset as outliers.
            if(N_obs//2 <= n_suspect):
                # print( 'no more datapoints can be rejected (n_suspect is N_obs/2 or more)')
                break

            # Compute R-value for the current number of suspect datapoints (`n_suspect`)
            # Parameters to PeirceBisect are N_obs, n_suspect, m_unknown
            R_threshold = self.PeirceBisect(N_obs, n_suspect, m_unknown) # Original m is m_unknown

            if R_threshold is None: # PeirceBisect failed to find a root
                # print(f'PeirceBisect failed for N_obs={N_obs}, n_suspect={n_suspect}, m_unknown={m_unknown}. Stopping.')
                break # Cannot proceed without R
            
            # Debug print from original code (parameters were delta, sigma, R_threshold):
            # print( delta <= sigma*R_threshold, sigma*R_threshold)
            
            # Determine how many datapoints are rejected by the current R_threshold
            # These are potential outliers based on current R_threshold.
            # Original name for current_rejected_count was Rej2.
            current_RejVec_temp = delta > sigma*R_threshold 
            current_rejected_count = np.sum(current_RejVec_temp)

            # If the number of points rejected by this R_threshold (`current_rejected_count`)
            # is greater than the number of points rejected in the previous successful 
            # iteration (`prev_rejected_count`), then we accept this new set of outliers.
            if(current_rejected_count > prev_rejected_count):
                # Update the class attributes to store this result as the current best set of outliers
                self.RejVec = current_RejVec_temp
                self.AcceptVec = np.logical_not(self.RejVec) 
                self.x2 = x_data[self.AcceptVec] # x2 is the filtered dataset
                
                prev_rejected_count = current_rejected_count # Update count of confirmed outliers
                
                n_suspect += 1 # Increment n_suspect for the next iteration (matches original `n += 1`)

            else: # current_rejected_count <= prev_rejected_count
                # print('number rejected datapoints not increasing with current R_threshold')
                break # Terminate the process
        
        try:
            if prev_rejected_count == 0: # No outliers were ever confirmed
                 self.x2 = x_data
                 self.RejVec = np.zeros(N_obs, dtype=bool)
                 self.AcceptVec = np.ones(N_obs, dtype=bool)
            # Else: attributes (x2, RejVec, AcceptVec) are already set from the last successful step.
        except UnboundLocalError: 
            self.x2 = x_data
            self.RejVec = np.zeros(N_obs, dtype=bool)
            self.AcceptVec = np.ones(N_obs, dtype=bool)


    def PeirceFunc(self, N_obs, n_rej, m_unknown, R_val_candidate):
        # Original signature: (self, N, n, m, x)
        """
        Evaluate the core function for Peirce's Criterion to find its roots.

        This function, denoted f(R), is derived from the probabilistic basis
        of Peirce's Criterion. The roots of f(R) = 0 provide the critical
        R-values used as thresholds for outlier rejection. The original simple
        docstring for this method was:
        ''' function to evalute in order to find roots for Peirce's criterion
            N - number of data samples
            n - number of data samples to be rejected
            m - number of independent variables (typically m=1)
            x - "R" value to be found, which is roots of function f'''
        In this docstring, `N_obs` corresponds to `N`, `n_rej` to `n`,
        `m_unknown` to `m`, and `R_val_candidate` to `x` from the original.

        Parameters
        ----------
        N_obs : int
            Total number of observations (data samples). (Corresponds to `N` in signature)
        n_rej : int
            Number of data samples suspected to be outliers (for which R is being calculated). (Corresponds to `n` in signature)
        m_unknown : int
            Number of unknown quantities. (Corresponds to `m` in signature)
        R_val_candidate : float
            The value of "R" (ratio of maximum allowable error to standard
            deviation) for which the function is to be evaluated. This is the
            variable for which the root is sought. (Corresponds to `x` in signature)

        Returns
        -------
        float
            The value of Peirce's function f(R). The bisection method will
            try to find `R_val_candidate` such that this return value is close to zero.
            Returns `np.inf` or `-np.inf` if `R_val_candidate` leads to invalid
            mathematical operations (e.g., log of non-positive, sqrt of negative),
            which helps guide the bisection algorithm.
        """
        # print(m_unknown) # Original debug print `print m` in the code

        if n_rej <= 0 or (N_obs - n_rej) <= 0 or N_obs <= 0:
            return np.inf 

        logQN = n_rej*np.log(n_rej) + \
                (N_obs-n_rej)*np.log(N_obs-n_rej) - \
                N_obs*np.log(N_obs)
        
        lamb_numerator = (N_obs - m_unknown - n_rej * R_val_candidate * R_val_candidate)
        lamb_denominator = (N_obs - m_unknown - n_rej)

        if lamb_numerator <= 0 or lamb_denominator <= 0:
            return np.inf 

        lamb = np.sqrt(lamb_numerator/lamb_denominator)

        erfc_input = R_val_candidate / np.sqrt(2)
        erfc_val = sp.erfc(erfc_input)
        
        if erfc_val <= 1e-300: 
            log_erfc_term = -np.inf 
        else:
            log_erfc_term = n_rej * np.log(erfc_val)
        
        if (np.isinf(log_erfc_term) and log_erfc_term < 0) or \
           (lamb > 0 and np.isinf(np.log(lamb)) and np.log(lamb) < 0) : # Check if log(lambda) is -inf
             f_value = -np.inf
        elif lamb == 0 and (N_obs-n_rej) > 0 : # log(lambda) is -inf if lambda is 0
             f_value = -np.inf
        else:
            f_value = (N_obs-n_rej)*np.log(lamb) + \
                      0.5*n_rej*(R_val_candidate*R_val_candidate-1) + \
                      log_erfc_term - logQN
        
        return f_value
        
    def PeirceBisect(self, N_obs, n_rej, m_unknown):
        # Original signature: (self, N, n, m)
        """
        Use bisection algorithm to find the R-value of Peirce's criterion.

        This method numerically solves for R where `PeirceFunc(N_obs, n_rej, m_unknown, R) = 0`.
        The R-value is a threshold: data points whose deviation from the mean,
        normalized by the standard deviation, exceeds R are considered outliers.
        The original simple docstring for this method was:
        ''' bisection algorithm for determining "R" values of Peirce's criterion'''
        In this docstring, `N_obs` corresponds to `N`, `n_rej` to `n`,
        and `m_unknown` to `m` from the original simple docstring and method signature.

        Parameters
        ----------
        N_obs : int
            Total number of observations. (Corresponds to `N` in signature)
        n_rej : int
            Number of data samples suspected to be outliers for this calculation of R. (Corresponds to `n` in signature)
        m_unknown : int
            Number of unknown quantities. (Corresponds to `m` in signature)

        Returns
        -------
        float or None
            The calculated R-value if a root is found within the given
            constraints and precision. Returns None if no root is found,
            if input parameters are invalid, or if the bisection algorithm
            fails to converge or encounters ill-defined regions.
        """
        eps = 2E-12 # precision epsilon for convergence
        xl = 0.1 # Lower bound for R. Original code used 1.0.

        if n_rej <= 0 or (N_obs - m_unknown) <= 0: return None
        
        xr_candidate_sq_num = (N_obs - m_unknown)
        xr_candidate_sq_den = float(n_rej)
        if xr_candidate_sq_num / xr_candidate_sq_den <= 0 : return None
            
        xr_candidate_sq = xr_candidate_sq_num / xr_candidate_sq_den
        if xr_candidate_sq <= xl**2: return None 

        xr = np.sqrt(xr_candidate_sq) - eps 
        if xl >= xr : return None

        func_xl = self.PeirceFunc(N_obs, n_rej, m_unknown, xl)
        func_xr = self.PeirceFunc(N_obs, n_rej, m_unknown, xr)

        if np.isnan(func_xl) or np.isnan(func_xr) or \
           np.isinf(func_xl) or np.isinf(func_xr) or \
           (func_xl * func_xr > 0):
            # Original print: print( 'No root exists with R < 1, for N = %.0d, n = %.0d and m = %.0d'.format(N_obs,n_rej,m_unknown))
            return None 
            
        xo = (xl+xr)/2.0 
        func_xo = self.PeirceFunc(N_obs, n_rej, m_unknown, xo)
        
        iter_count = 0
        max_iters = 100 
        while(abs(func_xo) > eps and iter_count < max_iters):
            if np.isinf(func_xo) or np.isnan(func_xo): return None 

            if(func_xl * func_xo < 0): 
                xr = xo
            else: 
                xl = xo
                func_xl = func_xo 
            
            xo = (xl+xr)/2.0
            func_xo = self.PeirceFunc(N_obs, n_rej, m_unknown, xo)
            iter_count +=1
        
        if iter_count >= max_iters and abs(func_xo) > eps: return None

        R_found = xo
        return R_found
        
if __name__ == "__main__":
    m_unknown_example = 1 # Example: 1 unknown quantity (e.g., the mean)
    
    print("\n--- Test Case 1 (Original Example from Script) ---")
    x_data1 = [4.24,3.94,3.85,3.82,3.60]
    print("Original data:", x_data1)
    test1_PC = PeirceCriteria(x_data1, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test1_PC.x2)
    print("Rejected points mask (RejVec):", test1_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test1_PC.AcceptVec)
    # Original script also called PeirceBisect directly:
    # r_example_direct = test1_PC.PeirceBisect(N_obs=5, n_rej=2, m_unknown=1) 
    # print(f"Example R-value from direct call to PeirceBisect(5,2,1): {r_example_direct}")

    print("\n--- Test Case 2 (Data from a different example) ---")
    x_data2 = [101.2, 90.0, 99.0, 102.0, 103.0, 100.2, 89.0, 98.1, 101.5, 102.0] # N=10
    print("Original data:", x_data2)
    test2_PC = PeirceCriteria(x_data2, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test2_PC.x2)
    print("Rejected points mask (RejVec):", test2_PC.RejVec) 
    print("Accepted points mask (AcceptVec):", test2_PC.AcceptVec)

    print("\n--- Test Case 3 (Obvious Outlier) ---")
    x_data3 = [10, 11, 10.5, 11.5, 10.8, 25.0] # N=6
    print("Original data:", x_data3)
    test3_PC = PeirceCriteria(x_data3, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test3_PC.x2)
    print("Rejected points mask (RejVec):", test3_PC.RejVec) 
    print("Accepted points mask (AcceptVec):", test3_PC.AcceptVec)

    print("\n--- Test Case 4 (No Obvious Outlier) ---")
    x_data4 = [10, 10.2, 10.1, 10.3, 9.9, 10.0, 10.15, 9.95] # N=8
    print("Original data:", x_data4)
    test4_PC = PeirceCriteria(x_data4, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test4_PC.x2)
    print("Rejected points mask (RejVec):", test4_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test4_PC.AcceptVec)

    print("\n--- Test Case 5 (Few Data Points) ---")
    x_data5 = [10, 11, 20] # N=3
    print("Original data:", x_data5)
    test5_PC = PeirceCriteria(x_data5, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test5_PC.x2)
    print("Rejected points mask (RejVec):", test5_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test5_PC.AcceptVec)
    
    print("\n--- Test Case 6 (Identical Data Points) ---")
    x_data6 = [5, 5, 5, 5, 5] # N=5
    print("Original data:", x_data6)
    test6_PC = PeirceCriteria(x_data6, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test6_PC.x2)
    print("Rejected points mask (RejVec):", test6_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test6_PC.AcceptVec)

    print("\n--- Test Case 7 (Two Groups) ---")
    x_data7 = [1, 2, 3, 10, 11, 12] # N=6
    print("Original data:", x_data7)
    test7_PC = PeirceCriteria(x_data7, m_unknown_example) 
    print("Data after Peirce's Criterion (x2):", test7_PC.x2)
    print("Rejected points mask (RejVec):", test7_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test7_PC.AcceptVec)

    print("\n--- Test Case 8 (Potentially problematic for internal math) ---")
    # e.g. N_obs - m_unknown - n_rej becomes zero or negative in lambda denominator in PeirceFunc
    # For N=3, m=1, if n_rej=2, then N-m-n = 3-1-2 = 0.
    x_data8 = [1, 2, 100] # N=3
    print("Original data:", x_data8)
    test8_PC = PeirceCriteria(x_data8, m_unknown_example)
    print("Data after Peirce's Criterion (x2):", test8_PC.x2)
    print("Rejected points mask (RejVec):", test8_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test8_PC.AcceptVec)

    # Example with m=2 (e.g. mean and std dev considered unknowns derived from sample)
    print("\n--- Test Case 9 (Example with m=2) ---")
    x_data9 = [10, 11, 10.5, 11.5, 10.8, 25.0, 26.0] # N=7
    print("Original data:", x_data9)
    test9_PC = PeirceCriteria(x_data9, m_unknown=2) 
    print("Data after Peirce's Criterion (x2):", test9_PC.x2)
    print("Rejected points mask (RejVec):", test9_PC.RejVec)
    print("Accepted points mask (AcceptVec):", test9_PC.AcceptVec)
