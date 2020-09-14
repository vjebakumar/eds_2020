import pandas as pd
import numpy as np

from datetime import datetime

from scipy import optimize
from scipy import integrate

%matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt
########################################

def SIR_model(SIR,beta,gamma,N0):
    '''Simple SIR model
        S: susceptible population
        I: infected population
        R: recovered population
        beta: infection rate
        gamma: recovery rate
        N0: Total population

        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)

     Parameters:
        ----------
        SIR : numpy.ndarray
        beta: float
        gamma: float
    '''

    S,I,R = SIR
    dS_dt=-beta*S*I/N0
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return(dS_dt,dI_dt,dR_dt)


if __name__ == '__main__':

    pd_JH_data=pd.read_csv('../data/processed/COVID_relational_confirmed.csv',sep=';',parse_dates=[0])
    pd_JH_data=pd_JH_data.sort_values('date',ascending=True).copy()
