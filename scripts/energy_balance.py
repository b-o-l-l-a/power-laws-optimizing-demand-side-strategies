import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import math
import argparse

import utils

git_root_path = utils.get_git_root(os.getcwd())
viz_root_path = os.path.join(git_root_path, utils.VIZ_DIR_NAME)
data_path = os.path.join(git_root_path, utils.DATA_DIR_NAME)

training_csv_path = os.path.join(data_path, utils.TRAINING_FILENAME + "." + utils.INPUT_DATA_FORMAT)

def energy_balance_plots(args):
    
    training_df = utils.clean_full_training_df(training_csv_path)
    training_df["energy_balance"] = training_df["actual_pv"] - training_df["actual_consumption"]
    sites = training_df["site_id"].unique()
    
    for site in sites:
        site_df = utils.clean_subsetted_df(training_df, "site_id", site)
        periods = site_df["period_id"].unique()
        for period in periods:
            
            period_df = utils.clean_subsetted_df(site_df, "period_id", period, True)
            
            create_and_save_plots(period_df, site, period, args)
            
def create_and_save_plots(df, site, period, args):
    
    num_viz = args.num_panels
    viz_duration = math.ceil((max(df.index) - min(df.index)).days / num_viz)
    start_timestamp = min(df.index)
    
    # TODO: put in config
    fig_height = 10
    sns.set(rc={'figure.figsize':(18, 10)})
    
    fig = plt.figure()

    ymin = min(df.energy_balance) 
    ymin = ymin - (abs(ymin) * .1)
    ymax = max(df.energy_balance)
    ymax = ymax + (abs(ymax) * .1)
    
    for i in range(1, num_viz + 1):
        start_dt_str = start_timestamp.strftime('%m-%d-%Y')
        end_dt_str = (start_timestamp + timedelta(days=viz_duration)).strftime('%m-%d-%Y')
        viz_df = df[(df.index >= start_timestamp) \
            & (df.index < start_timestamp + timedelta(days=viz_duration))]

        indiv_plot = fig.add_subplot(num_viz, 1, i)
        indiv_plot.set_ylim([ymin,ymax])
        indiv_plot = plt.plot('energy_balance', data=viz_df, linewidth=1, label="Energy Balance")
        viz_df['zeroes'] = 0.
        viz_df['timestamp'] = viz_df.index
        indiv_plot = plt.fill_between(viz_df.index,viz_df['energy_balance'],where=viz_df['energy_balance']>=viz_df['zeroes'], interpolate=True, color='black')
        indiv_plot = plt.fill_between(viz_df.index, viz_df['energy_balance'], where=viz_df['energy_balance']<=viz_df['zeroes'], interpolate=True, color='red')
        indiv_plot = plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
        indiv_plot = plt.title("Site ID: {site} / Period ID: {period} \n{start_dt_str} - {end_dt_str}".format(**locals()))

        fig.subplots_adjust(hspace = 0.5)
        del(indiv_plot)

        start_timestamp = start_timestamp + timedelta(days=viz_duration)

    viz_dir = os.path.join(viz_root_path, "energy_balance", "Site {}".format(site), "")
    filename = "Period {}.png".format(period)
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    plt.tight_layout()
    fig.savefig(os.path.join(viz_dir, filename))
    plt.close(fig)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create visualizations.')
    parser.add_argument("--num_panels", type=int, default=3, help="")
    args = parser.parse_args()
    print(args)
    energy_balance_plots(args)