import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt

def get_project_refactor(refactoring_miner):
    projects_refactor = {}

    for i in refactoring_miner.PROJECT_ID.unique():
        aux = {}
        for j in refactoring_miner.REFACTORING_TYPE.unique():
            faults = len(refactoring_miner[(refactoring_miner.PROJECT_ID==i) & (refactoring_miner.REFACTORING_TYPE==j)]["COMMIT_HASH"].unique())
            aux[j] = faults
        projects_refactor[i] = aux

    return projects_refactor


def get_project_faults(refactoring_miner, szz_fault_inducing_commits, fault_commits):
    projects_faults = {}

    for i in szz_fault_inducing_commits.PROJECT_ID.unique():
        aux = {}
        for j in refactoring_miner.REFACTORING_TYPE.unique():
            faults = len(fault_commits[(fault_commits.PROJECT_ID==i) & (fault_commits.REFACTORING_TYPE==j)]["FAULT_INDUCING_COMMIT_HASH"].unique())
            aux[j] = faults
        projects_faults[i] = aux

    return projects_faults


def plot_refactor_faults(projects_refactor, projects_faults, project_id):
    refact = pd.Series(pd.DataFrame(projects_refactor)[project_id], name="Refactor")
    faults = pd.Series(pd.DataFrame(projects_faults)[project_id], name="Faults")

    pd.concat([refact, faults], axis=1).plot(kind='bar', figsize=(18,7), rot=75, width=0.65, fontsize=17, color=('cornflowerblue','gold'),edgecolor = 'silver')
    plt.title(project_id, fontsize=20)
    plt.legend(fontsize=20)
    plt.show()
    

def plot_monthly_commits(git_commits, project_id):
    data = git_commits[git_commits.PROJECT_ID == project_id][['COMMITTER_DATE']]
    plt.figure(figsize=(20,10))
    plt.hist(pd.to_datetime(data['COMMITTER_DATE']).dt.to_period('M').astype(str), bins=len(pd.to_datetime(data['COMMITTER_DATE']).dt.to_period('M').astype(str).unique()),
            color=('cornflowerblue'),edgecolor = 'silver')
    plt.xticks(pd.to_datetime(data['COMMITTER_DATE']).dt.to_period('M').astype(str).unique()[::5], rotation=70)
    plt.title('Monthly commits of: ' + project_id, size=18)
    plt.ylabel('Number of commits', size=14)
    plt.xlabel('Month', size=14)
    plt.show()
