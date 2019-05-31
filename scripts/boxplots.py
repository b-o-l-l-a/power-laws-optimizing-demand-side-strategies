import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import math
import itertools
import numpy as np

import utils

git_root_path = utils.get_git_root(os.getcwd())
viz_root_path = os.path.join(git_root_path, utils.VIZ_DIR_NAME)
data_path = os.path.join(git_root_path, utils.DATA_DIR_NAME)

training_csv_path = os.path.join(data_path, utils.TRAINING_FILENAME + "." + utils.INPUT_DATA_FORMAT)

def create_forecast_accuracy_boxplots():
    training_df = pd.read_csv(training_csv_path, sep = ";")
    training_df["timestamp"] = pd.to_datetime(training_df["timestamp"])
    
    sites = training_df["site_id"].unique()
    
    for site in sites:
        boxplot_by_site(training_df, site)
        
def boxplot_by_site(df, site):
    
    site_df = df[df["site_id"] == site]
    site_df = site_df.sort_values("timestamp")
    #site_df = site_df.set_index("timestamp")
    
    periods = site_df["period_id"].unique()
    
    print("site ID {}".format(site))
    for period in periods:
        boxplot_by_period(site_df, site, period)
        
def boxplot_by_period(df, site, period):
    
    period_df = df[df["period_id"] == period].reset_index(drop=True)
    period_df["period_idx"] = period_df.index
    period_df = period_df.set_index(["timestamp"])
    start_timestamp = min(period_df.index)
    print("-- period ID {}".format(period))

    fig = plt.figure()
    for i in range(0, 10):
        print("---- calculating error for {} mins prev".format((i + 1) * 15))
        period_df["load_forecast_error_0{}_nominal".format(i)] = period_df.apply(lambda row: forecast_error(\
            period_df[period_df["period_idx"] == int(row["period_idx"]) - 1 - i]["load_0{}".format(i)].values[0],\
            row["actual_consumption"])\
            if row["period_idx"] > i else None, \
            axis= 1)

        period_df["pv_forecast_error_0{}_nominal".format(i)] = period_df.apply(lambda row: forecast_error(\
            period_df[period_df["period_idx"] == int(row["period_idx"]) - 1 - i]["pv_0{}".format(i)].values[0],\
            row["actual_pv"])\
            if row["period_idx"] > i else None, \
            axis= 1)

        period_df["load_forecast_error_0{}_perc".format(i)] = period_df["load_forecast_error_0{}_nominal".format(i)] / period_df["actual_consumption"]
        period_df["pv_forecast_error_0{}_perc".format(i)] = period_df["pv_forecast_error_0{}_nominal".format(i)] / period_df["actual_pv"]  
    
    period_df = period_df.replace(np.nan, 0)
    period_df = period_df.replace([np.inf, -np.inf], np.nan)
              
    sns.set(rc={'figure.figsize':(20, 13)})
    boxplot_xticks = ["{} mins".format((i + 1)* 15) for i in range(0, 10)]
    
    fig = plt.figure()
    plt.suptitle("Site {} / Period {}".format(site, period), fontsize=25)
    load_nom_boxplot = fig.add_subplot(4, 1, 1)
    load_nom_cols = [col for col in period_df if "load_forecast" in col and "nominal" in col]
    load_nom_boxplot = period_df[load_nom_cols].boxplot(showfliers=False)
    plt.xticks([i for i in range(1,11)], boxplot_xticks)
    load_nom_boxplot.set_title('Load forecast error (W)', fontsize=18)
    load_nom_boxplot = load_nom_boxplot.get_figure()

    load_perc_cols = [col for col in period_df if "load_forecast" in col and "perc" in col]
    load_perc_boxplot = fig.add_subplot(4, 1, 2)
    load_perc_boxplot = period_df[load_perc_cols].boxplot(showfliers=False)
    plt.xticks([i for i in range(1,11)], boxplot_xticks)
    load_perc_boxplot.set_title('Load forecast error (%)', fontsize=18)
    load_perc_boxplot = load_perc_boxplot.get_figure()

    pv_nom_cols = [col for col in period_df if "pv_forecast" in col and "nominal" in col]

    pv_nom_boxplot = fig.add_subplot(4, 1, 3)
    pv_nom_boxplot = period_df[pv_nom_cols].boxplot(showfliers=False , patch_artist=True)
    plt.xticks([i for i in range(1,11)], boxplot_xticks)

    pv_nom_boxplot.set_title('PV forecast error (W)', fontsize=18)
    pv_nom_boxplot = pv_nom_boxplot.get_figure()
    pv_perc_cols = [col for col in period_df if "pv_forecast" in col and "perc" in col]
    pv_perc_boxplot = fig.add_subplot(4, 1, 4)
    pv_perc_boxplot = period_df[pv_perc_cols].boxplot(showfliers=False, patch_artist=True)
    plt.xticks([i for i in range(1,11)], boxplot_xticks)
    pv_perc_boxplot.set_title('PV forecast error (%)', fontsize=18)
    pv_perc_boxplot = pv_perc_boxplot.get_figure()

    plt.tight_layout()
    fig.subplots_adjust(top = 0.92, hspace=0.3)
    
    viz_dir = os.path.join(viz_root_path, "forecast_errors", "Site {}".format(site), "")
    filename = "Period {}.png".format(period)
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
            
    fig.savefig(os.path.join(viz_dir, filename))
    plt.close(fig)


    
def forecast_error(predicted_val, true_val):

    return_val = predicted_val - true_val
    
    return return_val


if __name__ == "__main__":
    create_forecast_accuracy_boxplots()