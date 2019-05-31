import git
import pandas as pd

DATA_DIR_NAME = 'data'
OUTPUT_DIR_NAME = 'output'
VIZ_DIR_NAME = 'visualizations'

INPUT_DATA_FORMAT = 'csv'
TRAINING_FILENAME = 'power-laws-optimizing-demand-side-strategies-training-data'
SUBMIT_FILENAME = 'power-laws-optimizing-demand-side-strategies-submit-data'
SUBMISSION_FORMAT_FILENAME = 'power-laws-optimizing-demand-side-strategies-submission-format'
METADATA_FILENAME = 'power-laws-optimizing-demand-side-strategies-metadata'

def get_git_root(path):
    
    git_repo = git.Repo(path, search_parent_directories=True)
    
    return git_repo.working_dir

def clean_full_training_df(path):
    
    training_df = pd.read_csv(path, sep = ";")
    training_df["timestamp"] = pd.to_datetime(training_df["timestamp"])
    
    return training_df

def clean_subsetted_df(df, subset_id_col, subset_id, timestamp_to_index = False):
    
    subsetted_df = df[df[subset_id_col] == subset_id]
    
    if timestamp_to_index == True:
        subsetted_df = subsetted_df.sort_values("timestamp")
        subsetted_df = subsetted_df.set_index("timestamp")
        
    return subsetted_df
    