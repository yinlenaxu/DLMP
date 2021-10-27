# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import sqlite3
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def preprocess(git_commits, szz_fault_inducing_commits, refactoring_miner, git_commits_changes,inter_output_filepath, output_filepath):
    '''
    Returns a preprocessed dataframe
    :Params:
        - dataframe: git_commits (coming from GIT_COMMITS table from td_VD_2.db)
        - dataframe: szz_fault_inducing_commits (coming from SZZ_FAULT_INDUCING_COMMITS table from td_VD_2.db)
        - dataframe: refactoring_miner (coming from RERFACTORING_MINER table from td_VD_2.db)
        - dataframe: git_commits_changes (coming from GIT_COMMITS_CHANGES table from td_VD_2.db)
    :Return:
        - A dataframe containing the refactors that have induced faults including information about the commit
          This dataframe is thought to be used to train models to predict whether a refactor is going to induce a fault or not
    '''

    # keep columns and rows of interest of each dataframe individually and change formats

    git_commits = git_commits[['PROJECT_ID','COMMIT_HASH','COMMIT_MESSAGE','COMMITTER_DATE','BRANCHES']]
    szz_fault_inducing_commits = szz_fault_inducing_commits[["FAULT_FIXING_COMMIT_HASH", "FAULT_INDUCING_COMMIT_HASH"]]
    refactoring_miner = refactoring_miner[["COMMIT_HASH", "REFACTORING_TYPE"]].drop_duplicates(ignore_index=True)
    git_commits_changes = git_commits_changes[git_commits_changes["COMMIT_HASH"].isin(refactoring_miner["COMMIT_HASH"])]
    git_commits_changes = git_commits_changes[["PROJECT_ID", "COMMIT_HASH","LINES_ADDED","LINES_REMOVED"]]
    git_commits_changes["LINES_ADDED"] = git_commits_changes["LINES_ADDED"].astype(int)
    git_commits_changes["LINES_REMOVED"] = git_commits_changes["LINES_REMOVED"].astype(int)
    git_commits_changes = git_commits_changes.groupby(['COMMIT_HASH', "PROJECT_ID"]).sum().reset_index()

    git_commits['NUM_COMMIT'] = 0
    for proj in git_commits.PROJECT_ID.unique().tolist():
        max_comm = len(git_commits[git_commits.PROJECT_ID == proj])
        git_commits.loc[git_commits.PROJECT_ID == proj, 'NUM_COMMIT'] = list(range(max_comm))

    first_commit = {}
    for proj in git_commits.PROJECT_ID.unique().tolist():
        if proj in ['org.apache:batik','org.apache:cocoon','org.apache:felix','org.apache:santuario']:
            pass
        else:
            git_commits.loc[git_commits.PROJECT_ID == proj, 'COMMITTER_DATE'] = git_commits['COMMITTER_DATE'].apply(lambda x: str(x)[:-6])
        first_commit[proj] = pd.to_datetime(git_commits[git_commits.PROJECT_ID == proj]['COMMITTER_DATE'].min()).date()
        git_commits.loc[git_commits.PROJECT_ID == proj,'COMMITTER_DATE'] = pd.to_datetime(git_commits.loc[git_commits.PROJECT_ID == proj,'COMMITTER_DATE'], dayfirst=True).dt.date
        git_commits.loc[git_commits.PROJECT_ID == proj,'COMMIT_DAY'] = git_commits.loc[git_commits.PROJECT_ID == proj,'COMMITTER_DATE'] - first_commit[proj]
    git_commits['COMMIT_DAY'] = git_commits['COMMIT_DAY'].apply(lambda x: x.days)

    # git_commits_changes preprocess

    git_commits_changes = git_commits_changes.merge(git_commits[['COMMIT_HASH','NUM_COMMIT', "COMMIT_DAY"]], on = 'COMMIT_HASH')
    git_commits_changes = git_commits_changes.sort_values(["PROJECT_ID", "NUM_COMMIT"]).reset_index().drop("index", axis=1)
    git_commits_changes['LINES_ADDED_LAST_COMMITS'] = 0
    git_commits_changes['LINES_REMOVED_LAST_COMMITS'] = 0

    days = 5
    for i in range(len(git_commits_changes)):
        git_commits_changes.loc[i, "LINES_ADDED_LAST_COMMITS"] = git_commits_changes.loc[i-days:i-1, "LINES_ADDED"][git_commits_changes.PROJECT_ID == git_commits_changes.loc[i, "PROJECT_ID"]].sum()
        git_commits_changes.loc[i, "LINES_REMOVED_LAST_COMMITS"] = git_commits_changes.loc[i-days:i-1, "LINES_REMOVED"][git_commits_changes.PROJECT_ID == git_commits_changes.loc[i, "PROJECT_ID"]].sum()

    # refactor_commits preprocess

    refactor_commits = refactoring_miner[["COMMIT_HASH", "REFACTORING_TYPE"]].merge(git_commits_changes[["COMMIT_HASH", "COMMIT_DAY", "LINES_ADDED", "LINES_REMOVED", "LINES_ADDED_LAST_COMMITS", "LINES_REMOVED_LAST_COMMITS"]], on = "COMMIT_HASH")
    refactor_commits["LINES_ADDED"] = refactor_commits["LINES_ADDED"].astype(int)
    refactor_commits["LINES_REMOVED"] = refactor_commits["LINES_REMOVED"].astype(int)

    refactor_commits["LABEL"] = 0
    refactor_commits["LABEL"] = np.where(refactor_commits["COMMIT_HASH"].isin(szz_fault_inducing_commits["FAULT_INDUCING_COMMIT_HASH"]), 1, 0)

    # merge of dataframes
    refactoring_fault_inducing = refactoring_miner.merge(szz_fault_inducing_commits, left_on="COMMIT_HASH", right_on="FAULT_INDUCING_COMMIT_HASH")
    refactoring_fault_inducing = refactoring_fault_inducing.drop("COMMIT_HASH", axis=1)
    fault_fixing_commits = refactoring_fault_inducing.merge(git_commits, left_on="FAULT_FIXING_COMMIT_HASH", right_on="COMMIT_HASH")
    fault_fixing_commits = fault_fixing_commits.drop("COMMIT_HASH", axis=1)

    # create csv file
    
    git_commits.to_csv(inter_output_filepath+'/git_commits.csv', index = False)
    szz_fault_inducing_commits.to_csv(inter_output_filepath+'/szz_fault_inducing_commits.csv', index = False)
    refactoring_miner.to_csv(inter_output_filepath+'/refactoring_miner.csv', index = False)
    git_commits_changes.to_csv(inter_output_filepath+'/git_commits_changes.csv', index = False)
    
    fault_fixing_commits.to_csv(output_filepath+'/fault_commits.csv', index = False)
    refactor_commits.to_csv(output_filepath+'/refactor_commits.csv', index = False)


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('inter_output_filepath', type=click.Path())
@click.argument('output_filepath', type=click.Path())
def main(input_filepath = '../../data/raw', inter_output_filepath = '../../data/interim', output_filepath = '../../data/processed'):  # modified
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    conn = sqlite3.connect(input_filepath+'/td_V2.db')
    git_commits = pd.read_sql_query("SELECT * FROM GIT_COMMITS",conn)
    szz_fault_inducing_commits = pd.read_sql_query("SELECT * FROM szz_fault_inducing_commits",conn)
    refactoring_miner = pd.read_sql_query("SELECT * FROM refactoring_miner",conn)
    refactoring_miner = refactoring_miner[refactoring_miner["COMMIT_HASH"].isin(git_commits["COMMIT_HASH"])]
    git_commits_changes = pd.read_sql_query("SELECT * FROM GIT_COMMITS_CHANGES", conn)
    git_commits_changes = git_commits_changes[git_commits_changes["COMMIT_HASH"].isin(refactoring_miner["COMMIT_HASH"])]

    preprocess(git_commits, szz_fault_inducing_commits, refactoring_miner, git_commits_changes,inter_output_filepath, output_filepath)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
