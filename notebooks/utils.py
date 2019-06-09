import git

DATA_DIR_NAME = 'data'
OUTPUT_DIR_NAME = 'output'
VIZ_DIR_NAME = 'visualizations'

INPUT_DATA_FORMAT = 'csv'
TRAINING_FILENAME = 'power-laws-optimizing-demand-side-strategies-training-data'
SUBMIT_FILENAME = 'power-laws-optimizing-demand-side-strategies-submit-data'
SUBMISSION_FORMAT_FILENAME = 'power-laws-optimizing-demand-side-strategies-submission-format'
METADATA_FILENAME = 'power-laws-optimizing-demand-side-strategies-metadata'

VIZ_DEFAULT_WIDTH = 18
VIZ_DEFAULT_HEIGHT = 9

def get_git_root(path):
    
    git_repo = git.Repo(path, search_parent_directories=True)
    
    return git_repo.working_dir
