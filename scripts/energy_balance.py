import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
        site_df = utils.clean_subsetted_df(training_df, "site_id", site, False)
        print("- site ID {}".format(site))
        periods = site_df["period_id"].unique()
        for period in periods:
            
            period_df = utils.clean_subsetted_df(site_df, "period_id", period, True)
            
            plot_energy_balance(period_df, site, period, args)
            
def plot_energy_balance(df, site, period, args):
    
    num_viz = args.num_panels
    viz_duration = math.ceil((max(df.index) - min(df.index)).days / num_viz)
    start_timestamp = min(df.index)
    print("-- period ID {}".format(period))

    sns.set(rc={'figure.figsize':(utils.VIZ_DEFAULT_WIDTH, utils.VIZ_DEFAULT_HEIGHT)})
    
    fig = plt.figure()

    plt.suptitle("Energy Balance and Price - Site ID: {site} / Period ID: {period}".format(**locals()), \
                 fontsize=20, fontweight="heavy")
    ymin = min(df.energy_balance) 
    ymin = ymin - (abs(ymin) * .1)
    ymax = max(df.energy_balance)
    ymax = ymax + (abs(ymax) * .1)
    
    df['zeroes'] = 0.

    viz_dir = os.path.join(viz_root_path, "energy_balance", "Site {}".format(site), "")
    filename = "Period {}.png".format(period)

    for i in range(1, num_viz + 1):
        start_dt_str = start_timestamp.strftime('%m-%d-%Y')
        end_dt_str = (start_timestamp + timedelta(days=viz_duration)).strftime('%m-%d-%Y')
        viz_df = df[(df.index >= start_timestamp) \
             & (df.index < start_timestamp + timedelta(days=viz_duration))]

        energy_bal_ax = fig.add_subplot(num_viz, 1, i)
        energy_bal_ax.set_ylim([ymin,ymax])
        energy_bal_ax.set_ylabel("Energy (W)")
        energy_bal_ax.plot('energy_balance', data=viz_df, linewidth=1, label="Energy Balance", alpha=0)
        energy_bal_ax.fill_between(viz_df.index,viz_df['energy_balance'],where=viz_df['energy_balance']>=viz_df['zeroes'], interpolate=True, color='black')
        energy_bal_ax.fill_between(viz_df.index, viz_df['energy_balance'], where=viz_df['energy_balance']<=viz_df['zeroes'], interpolate=True, color='red')
        energy_bal_ax.yaxis.grid(False)

        energy_bal_ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=range(1,32), interval=1))
        energy_bal_ax.xaxis.grid(True, linestyle="--", color="gray")

        price_ax = energy_bal_ax.twinx() 
        price_ax.set_ylabel('Buy Price ($)', color="green")
        price_ax.plot(viz_df['price_buy_00'], color="green", alpha = 0.5)
        price_ax.tick_params(axis='y', color="green")
        price_ax.yaxis.grid(False)

        plt.setp(price_ax.get_yticklabels(), color="green")
        plt.title("{start_dt_str} - {end_dt_str}".format(**locals()), fontdict={"fontsize": 16})
        fig.subplots_adjust(hspace = 0.5)
        if not os.path.exists(viz_dir):
            os.makedirs(viz_dir)
        plt.tight_layout()
        fig.savefig(os.path.join(viz_dir, filename))
        [i.set_color("red") for i in energy_bal_ax.get_yticklabels() if float(i.get_text().replace('−', '-')) < 0]
        start_timestamp = start_timestamp + timedelta(days=viz_duration)

    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    plt.tight_layout()
    fig.subplots_adjust(top = 0.9)
    fig.savefig(os.path.join(viz_dir, filename))
    plt.close(fig)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create visualizations.')
    parser.add_argument("--num_panels", type=int, default=3, help="")
    args = parser.parse_args()

    energy_balance_plots(args)