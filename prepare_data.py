import pandas as pd
import os

def separate_df_by_site(input_path, output_folder):
    
    df = pd.read_csv(input_path, sep=";")
    sites = df["site_id"].unique()
    print(sites)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for site in sites:
        print(site)
        site_df = df[df["site_id"] == site]
        site_df.to_csv(os.path.join(output_folder, '{}.csv'.format(site)))
    
    return

if __name__ == "__main__":

    root_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(root_dir, 'data')
    train_path = os.path.join(data_dir, 'power-laws-optimizing-demand-side-strategies-training-data.csv')
    test_path = os.path.join(data_dir, 'power-laws-optimizing-demand-side-strategies-submit-data.csv')
    
    print("separating training data to separate folder")
    separate_df_by_site(train_path, os.path.join(data_dir, 'train'))
    print("separating test data to separate folder")
    separate_df_by_site(train_path, os.path.join(data_dir, 'submit'))