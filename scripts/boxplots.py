import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import math
import itertools
import numpy as np
import argparse

import utils

git_root_path = utils.get_git_root(os.getcwd())
viz_root_path = os.path.join(git_root_path, utils.VIZ_DIR_NAME)
data_path = os.path.join(git_root_path, utils.DATA_DIR_NAME)

training_csv_path = os.path.join(data_path, utils.TRAINING_FILENAME + "." + utils.INPUT_DATA_FORMAT)
augmented_df_path = os.path.join(data_path, "{}-w-accuracy-cols.csv".format(utils.TRAINING_FILENAME))


min_perc_whisker = 10
max_perc_whisker = 90

def create_forecast_accuracy_boxplots(args):

    if args.create_cols == True: 
        
        training_df = utils.clean_full_training_df(training_csv_path)
        cleaned_training_df = create_augmented_df(training_df)
     
    else:
        cleaned_training_df = utils.clean_full_training_df(augmented_df_path)

    if args.site_plots == True:
        
        sites = cleaned_training_df["site_id"].unique()
        
        for site in sites:
            create_and_save_site_plot(cleaned_training_df, site)
    else:
        create_and_save_full_plots(cleaned_training_df)
    print("\nsuccessfully completed")

    
def create_and_save_full_plots(df):

    sns.set(rc={'figure.figsize':(16, 30)})
    num_plots = 10
    viz_dir = os.path.join(viz_root_path, "forecast_errors")
    
    load_fig, load_axes = plt.subplots(num_plots,2)

    load_nom_y_min = get_axis_lim(df, "min", "nominal", "load_forecast_error", True)
    load_nom_y_max = get_axis_lim(df, "max", "nominal", "load_forecast_error", True)
    load_perc_y_min = get_axis_lim(df, "min", "perc", "load_forecast_error", True) 
    load_perc_y_max = get_axis_lim(df, "max", "perc", "load_forecast_error", True) 
    
    for i in range(0,num_plots):

        nom_axis = load_axes.flatten()[i*2]
        nom_axis.set_ylim([load_nom_y_min,load_nom_y_max])
        df.boxplot(by='site_id', ax=nom_axis, \
                                    column = ["load_forecast_error_0{}_nominal".format(i)], \
                                    whis= [min_perc_whisker, max_perc_whisker],showfliers=False, patch_artist=True)
        nom_axis.xaxis.grid(False)
        nom_axis.set_title("Nominal load forecast error - {} mins".format((i + 1)* 15), fontsize=16)

        perc_axis = load_axes.flatten()[(i*2)+1]
        perc_axis.set_ylim([load_perc_y_min, load_perc_y_max])
        df.boxplot(by='site_id', ax=perc_axis, \
                                    column = ["load_forecast_error_0{}_perc".format(i)], \
                                    whis= [min_perc_whisker, max_perc_whisker],showfliers=False, patch_artist=False)
        perc_axis.xaxis.grid(False)
        perc_axis.set_title("Percentage load forecast error - {} mins".format((i + 1)* 15), fontsize=16)
      
    plt.suptitle("Load Forecast Errors by Site", fontsize=25)
    plt.tight_layout()
    load_fig.subplots_adjust(top = 0.95, hspace=0.4)    
    
    load_filename = "Load Errors by Site.png"
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    
    print("----- saving to {}".format(os.path.join(viz_dir, load_filename)))
    load_fig.savefig(os.path.join(viz_dir, load_filename))
    plt.close(load_fig)
    
    pv_nom_y_min = get_axis_lim(df, "min", "nominal", "pv_forecast_error", True)
    pv_nom_y_max = get_axis_lim(df, "max", "nominal", "pv_forecast_error", True)
    pv_perc_y_min = get_axis_lim(df, "min", "perc", "pv_forecast_error", True)
    pv_perc_y_max = get_axis_lim(df, "max", "perc", "pv_forecast_error", True)

    pv_fig, pv_axes = plt.subplots(num_plots,2)

    for i in range(0,num_plots):
        nom_axis = pv_axes.flatten()[i*2]
        nom_axis.set_ylim([pv_nom_y_min,pv_nom_y_max])
        df.boxplot(by='site_id', ax=nom_axis, \
            column = ["pv_forecast_error_0{}_nominal".format(i)], \
            whis= [min_perc_whisker, max_perc_whisker],showfliers=False, patch_artist=True)
        nom_axis.xaxis.grid(False)
        nom_axis.set_title("Nominal PV forecast error - {} mins".format((i + 1)* 15))

        perc_axis = pv_axes.flatten()[(i*2)+1]
        perc_axis.set_ylim([pv_perc_y_min, pv_perc_y_max])
        df.boxplot(by='site_id', ax=perc_axis, \
            column = ["pv_forecast_error_0{}_perc".format(i)], \
            whis= [min_perc_whisker, max_perc_whisker],showfliers=False, patch_artist=False)
        perc_axis.xaxis.grid(False)
        perc_axis.set_title("Percentage PV forecast error - {} mins".format((i + 1)* 15))
    plt.suptitle("PV Forecast Errors by Site", fontsize=25)
    plt.tight_layout()
    pv_fig.subplots_adjust(top = 0.95, hspace=0.4)    
    
    pv_filename = "PV Errors by Site.png"
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    
    print("----- saving to {}".format(os.path.join(viz_dir, pv_filename)))
    pv_fig.savefig(os.path.join(viz_dir, pv_filename))
    plt.close(load_fig)
    
def create_augmented_df(training_df):
    
    sites = training_df["site_id"].unique()
    cleaned_training_df = pd.DataFrame()
    for site in sites:
        print("- site ID {}".format(site))
        site_df = utils.clean_subsetted_df(training_df, "site_id", site, False)

        periods = site_df["period_id"].unique()
        cleaned_site_df = pd.DataFrame()

        for period in periods: 
            print("-- period ID: {}".format(period))
            period_df = utils.clean_subsetted_df(site_df, "period_id", period, True)
            period_df["period_idx"] = np.arange(period_df.shape[0])

            period_df = create_accuracy_cols(period_df)
            cleaned_site_df = cleaned_site_df.append(period_df)

        cleaned_site_df = cleaned_site_df.replace([np.inf, -np.inf], np.nan)
        cleaned_training_df = cleaned_training_df.append(cleaned_site_df)

    cols_to_keep = [["timestamp", "site_id", "period_id", "actual_consumption", "actual_pv", "price_buy_00"]]
    cols_to_keep.append([col for col in cleaned_training_df.columns if "forecast" in col])

    cols_to_keep = [item for sublist in cols_to_keep for item in sublist]
    cleaned_training_df["timestamp"] = cleaned_training_df.index
    cleaned_training_df[cols_to_keep].to_csv(augmented_df_path, sep = ";", index=False)    

    return cleaned_training_df

def create_and_save_site_plot(df, site):

    df = df[df["site_id"] == site]
    nom_cols = [col for col in df.columns if "nominal" in col]
    nom_y_max = df[nom_cols].quantile((max_perc_whisker / 100.)).max()
    nom_y_max = nom_y_max + (.1 * nom_y_max)
    nom_y_min = df[nom_cols].quantile((min_perc_whisker / 100.)).min()
    nom_y_min = nom_y_min - abs(.1 * nom_y_min)

    perc_cols = [col for col in df.columns if "perc" in col]
    perc_y_max = df[perc_cols].quantile((max_perc_whisker / 100.)).max()
    perc_y_max = perc_y_max + (.1 * perc_y_max)
    perc_y_min = df[perc_cols].quantile((min_perc_whisker / 100.)).min()
    perc_y_min = perc_y_min - abs(.1 * perc_y_min)
    
    sns.set(rc={'figure.figsize':(utils.VIZ_DEFAULT_WIDTH, utils.VIZ_DEFAULT_HEIGHT)})
    fig = plt.figure()
    plt.suptitle("Site {}".format(site), fontsize=25)
    print("---- creating subplots")
    load_nom_boxplot = fig.add_subplot(4, 1, 1)
    load_nom_cols = [col for col in df if "load_forecast" in col and "nominal" in col]
    plot_site_df(load_nom_boxplot, df[load_nom_cols], nom_y_min, nom_y_max, 'Load forecast error (W)', False)
    
    pv_nom_boxplot = fig.add_subplot(4, 1, 2)
    pv_nom_cols = [col for col in df if "pv_forecast" in col and "nominal" in col]
    plot_site_df(pv_nom_boxplot, df[pv_nom_cols], nom_y_min, nom_y_max, 'PV forecast error (W)')
    
    load_perc_boxplot = fig.add_subplot(4, 1, 3)
    load_perc_cols = [col for col in df if "load_forecast" in col and "perc" in col]
    plot_site_df(load_perc_boxplot, df[load_perc_cols], perc_y_min, perc_y_max, 'Load forecast error (%)', False)

    pv_perc_boxplot = fig.add_subplot(4, 1, 4)
    pv_perc_cols = [col for col in df if "pv_forecast" in col and "perc" in col]
    plot_site_df(pv_perc_boxplot, df[pv_perc_cols], perc_y_min, perc_y_max, 'PV forecast error (%)')
    
    plt.tight_layout()
    fig.subplots_adjust(top = 0.9, hspace=0.39)
    
    viz_dir = os.path.join(viz_root_path, "forecast_errors", "")
    filename = "Site {}.png".format(site)
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    
    print("----- saving to {}".format(os.path.join(viz_dir, filename)))
    fig.savefig(os.path.join(viz_dir, filename))
    plt.close(fig)
    
    
def plot_site_df(subplot, df, ymin, ymax, title, fill=True):
    
    boxplot_xticks = ["{} mins".format((i + 1)* 15) for i in range(0, 10)]
    
    df.boxplot(whis= [min_perc_whisker, max_perc_whisker],showfliers=False, patch_artist=fill)
    subplot.xaxis.grid(False)
    subplot.xaxis.grid(False)
    subplot.set_ylim([ymin,ymax])
    
    plt.xticks([i for i in range(1,11)], boxplot_xticks)
    
    subplot.set_title(title, fontsize=14)
    subplot.get_figure()
    
    return
    
def create_accuracy_cols(df):
    
    for i in range(0, 10):
        print("--- calculating error for {} mins prev".format((i + 1) * 15))
        df["load_forecast_error_0{}_nominal".format(i)] = df.apply(lambda row: forecast_error(\
            df[df["period_idx"] == int(row["period_idx"]) - 1 - i]["load_0{}".format(i)].values[0],\
            row["actual_consumption"])\
            if row["period_idx"] > i else None, \
            axis= 1)

        df["pv_forecast_error_0{}_nominal".format(i)] = df.apply(lambda row: forecast_error(\
            df[df["period_idx"] == int(row["period_idx"]) - 1 - i]["pv_0{}".format(i)].values[0],\
            row["actual_pv"])\
            if row["period_idx"] > i else None, \
            axis= 1)

        df["load_forecast_error_0{}_perc".format(i)] = df["load_forecast_error_0{}_nominal".format(i)] / df["actual_consumption"]
        df["pv_forecast_error_0{}_perc".format(i)] = df["pv_forecast_error_0{}_nominal".format(i)] / df["actual_pv"]  
        
    return df
    
def forecast_error(predicted_val, true_val):

    return_val = predicted_val - true_val
    
    return return_val

def get_axis_lim(df, max_or_min, perc_or_nom, col_substr, group_by_site_id = False):
    
    min_perc_whisker = 10
    max_perc_whisker = 90
    
    max_or_min_types = ['max', 'min']
    if max_or_min not in max_or_min_types:
        raise ValueError("Invalid max_or_min arg. Expected one of: {}".format(max_or_min_types))
    
    perc_or_nom_types = ["nominal", "perc"]
    if perc_or_nom not in perc_or_nom_types:
        raise ValueError("Invalid perc_or_nom arg. Expected one of: {}".format(perc_or_nom_types))
    
    whisker_lim = min_perc_whisker if max_or_min == "min" else max_perc_whisker
    
    cols = [col for col in df.columns if perc_or_nom in col and col_substr in col]
    if group_by_site_id == True:
        grp_by_df = df.groupby("site_id")[cols].quantile((whisker_lim / 100.)) #.max().max()
        
        ax_lim = grp_by_df.max().max() if max_or_min == "max" else grp_by_df.min().min()
    
    ax_lim = ax_lim + (.1 * ax_lim) if max_or_min == "max" else ax_lim - abs(.1 * ax_lim)
    
    return ax_lim

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create visualizations.')
    parser.add_argument("--create_cols", "-c", type=str, default="False", help="")
    parser.add_argument("--site_plots", "-s", type=str, default="False", help="")
    args = parser.parse_args()
    args.create_cols = True if args.create_cols.upper() == "TRUE" else False
    args.site_plots = True if args.site_plots.upper() == "TRUE" else False
    create_forecast_accuracy_boxplots(args)