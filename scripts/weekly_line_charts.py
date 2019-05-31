import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import math
import argparse
import json

import utils

git_root_path = utils.get_git_root(os.getcwd())
viz_root_path = os.path.join(git_root_path, utils.VIZ_DIR_NAME)
data_path = os.path.join(git_root_path, utils.DATA_DIR_NAME)

training_csv_path = os.path.join(data_path, utils.TRAINING_FILENAME + "." + utils.INPUT_DATA_FORMAT)

def create_weekly_plots(args):
    
    training_df = pd.read_csv(training_csv_path, sep = ";")
    training_df["timestamp"] = pd.to_datetime(training_df["timestamp"])
    
    sites = training_df["site_id"].unique()
    
    for site in sites:
        viz_by_site(training_df, site, args)
        
def viz_by_site(df, site, args):
    
    site_df = df[df["site_id"] == site]
    site_df = site_df.sort_values("timestamp")
    site_df = site_df.set_index("timestamp")
    
    periods = site_df["period_id"].unique()
    
    print("site ID {}".format(site))
    for period in periods:
        viz_by_period(site_df, site, period, args)
    
def viz_by_period(df, site, period, args):
    
    period_df = df[df["period_id"] == period]
    num_weeks = math.ceil((max(period_df.index) - min(period_df.index)).days / 7)
    plot_cols = args.col
    output_folder = args.output_folder
    
    start_timestamp = min(period_df.index)
    print("-- period ID {}".format(period))
    
    fig_height = 4 * num_weeks
    sns.set(rc={'figure.figsize':(14, fig_height)})
    
    fig = plt.figure()
    #fig.subplots_adjust(top = 2.0)
    for i in range(1, num_weeks + 1):
        start_dt_str = start_timestamp.strftime('%m-%d-%Y')
        end_dt_str = (start_timestamp + timedelta(days=7)).strftime('%m-%d-%Y')
        weekly_df = period_df[(period_df.index >= start_timestamp) \
            & (period_df.index < start_timestamp + timedelta(days=7))]
        
        weekly_plot = fig.add_subplot(num_weeks, 1, i)
        for col_dict in plot_cols:
            
            col_name = str(list(col_dict)[0])
            friendly_name = str(col_dict[col_name])
            weekly_plot = plt.plot(col_name, data=weekly_df, linewidth=1, label=friendly_name)
            #weekly_plot = plt.plot('actual_pv', data=weekly_df, linewidth=1, label="PV")
        
        weekly_plot = plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
        weekly_plot = plt.title("Site ID: {site} / Period ID: {period} \n{start_dt_str} - {end_dt_str}".format(**locals()))
        fig.subplots_adjust(hspace = 0.5)
        del(weekly_plot)
        
        start_timestamp = start_timestamp + timedelta(days=7)
        
    plt.tight_layout()
    viz_dir = os.path.join(viz_root_path, output_folder, "Site {}".format(site), "")
    filename = "Period {}.png".format(period)
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
            
    fig.savefig(os.path.join(viz_dir, filename))
    plt.close(fig)



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create visualizations.')
    parser.add_argument("output_folder", type=str, help="")
    parser.add_argument('--col', type=json.loads, action='append',
        help='an integer for the accumulator')
    args = parser.parse_args()
    print(args)
    create_weekly_plots(args)