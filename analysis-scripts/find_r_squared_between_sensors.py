# Imports
import pandas as pd
import ast
import scipy.stats
import sys
import csv

# NOTE: Currently designed for large files
# for use on smaller files, remove csv.field_size_limit(sys.maxsize)
# from main() and remove low_memory=False from read_csv pandas method

def display_rsquared_data(arg_list):

    # Create separate list that does not include frequency
    file_args = arg_list[:-1]

    # Declare dictionaries
    df_collection = {}
    data_time_collection = {}
    data_db_collection = {}

    # Set counter for dictionaries
    count = 0

    # Get the frequency from command line args
    frequency = int(arg_list[-1])

    # Loop through files from command line args
    for i in file_args:

        # Store dataframe in dictionary
        # NOTE: Assumes file(s) is/are in same directory as .py
        df_collection[count] = pd.read_csv(i, header=None, low_memory=False)

        # Give dataframe column names
        df_collection[count].columns = ["Date","Time","Hz Low","Hz High","Hz bin width","Num Samples","dB1","dB2","dB3","dB4","dB5"]

        # Make the Time column value strings
        df_collection[count]["Time"] = df_collection[count]["Time"].str.strip()

        #NOTE: Times are hardcoded as of now

        # Get list of indices with all rows that contain a specified time
        row1 = (df_collection[count])[df_collection[count]['Time'] == '12:52:00'].index.tolist()

        # Get list of indices with all rows that contain a specified time
        row2 = (df_collection[count])[df_collection[count]['Time'] == '12:57:00'].index.tolist()

        # Use these lists of indices and "filter" out every part of the
        # dataframe except for inbetween these indices.
        # This is how a certain time is analyzed
        df_collection[count] = df_collection[count].iloc[row1[0]:row2[0]]

        # Re-give dataframe columns in case they are lost by above filter
        df_collection[count].columns = ["Date","Time","Hz Low","Hz High","Hz bin width","Num Samples","dB1","dB2","dB3","dB4","dB5"]

        # Only keep rows that contain the desired frequency
        df_collection[count] = df_collection[count][df_collection[count]["Hz Low"] == frequency].reset_index(drop=True)

        # Make all dB measurements strings
        df_collection[count]['dB1'] = df_collection[count]['dB1'].astype(str)
        df_collection[count]['dB2'] = df_collection[count]['dB2'].astype(str)
        df_collection[count]['dB3'] = df_collection[count]['dB3'].astype(str)
        df_collection[count]['dB4'] = df_collection[count]['dB4'].astype(str)
        df_collection[count]['dB5'] = df_collection[count]['dB5'].astype(str)

        # Join every dB measurement together in case there are multiple
        # rows that have the same time and frequency
        df_collection[count] = df_collection[count].groupby('Time').agg({'dB1': ','.join, 'dB2': ','.join, 'dB3': ','.join, 'dB4': ','.join, 'dB5': ','.join}).reset_index()

        # Surround the now comma separated dB measurements with brackets to
        # easily convert into list
        df_collection[count]['dB1'] = '[' + df_collection[count]['dB1'] + ']'
        df_collection[count]['dB2'] = '[' + df_collection[count]['dB2'] + ']'
        df_collection[count]['dB3'] = '[' + df_collection[count]['dB3'] + ']'
        df_collection[count]['dB4'] = '[' + df_collection[count]['dB4'] + ']'
        df_collection[count]['dB5'] = '[' + df_collection[count]['dB5'] + ']'

        # Declare and initialize lists for times and dB measurements
        list_of_times = []
        list_of_dbs = []

        # Loop through dataframe
        for index, row in df_collection[count].iterrows():

            # Append the time to a list
            list_of_times.append(row["Time"])

            # Change every dB column value to its average
            df_collection[count].loc[index, 'dB1'] = sum(ast.literal_eval(row["dB1"]))/len(ast.literal_eval(row["dB1"]))
            df_collection[count].loc[index, 'dB2'] = sum(ast.literal_eval(row["dB2"]))/len(ast.literal_eval(row["dB2"]))
            df_collection[count].loc[index, 'dB3'] = sum(ast.literal_eval(row["dB3"]))/len(ast.literal_eval(row["dB3"]))
            df_collection[count].loc[index, 'dB4'] = sum(ast.literal_eval(row["dB4"]))/len(ast.literal_eval(row["dB4"]))
            df_collection[count].loc[index, 'dB5'] = sum(ast.literal_eval(row["dB5"]))/len(ast.literal_eval(row["dB5"]))

        # Loop through dataframe again
        for index, row in df_collection[count].iterrows():

            # Declare and initialize a sub list for each dB measurement
            db_sub_list = []

            # Append every dB average to this sub list
            db_sub_list.append(row["dB1"])
            db_sub_list.append(row["dB2"])
            db_sub_list.append(row["dB3"])
            db_sub_list.append(row["dB4"])
            db_sub_list.append(row["dB5"])

            # Append the average of every dB average into a list
            list_of_dbs.append(sum(db_sub_list)/len(db_sub_list))

        # Add time and dB measurements to dictionary
        data_time_collection[count] = list_of_times
        data_db_collection[count] = list_of_dbs

        # Increment counter
        count += 1

    print("Result:\n")

    # Loop through file args
    for i in file_args:

        first_sample_count = file_args.index(i)

        # Loop through again to compare every dataset to each other
        for j in file_args[first_sample_count:]:

            second_sample_count = file_args.index(j)

            if first_sample_count != second_sample_count:

                # Get r squared
                r_squared = scipy.stats.pearsonr(data_db_collection[first_sample_count], data_db_collection[second_sample_count])[0]**2

                # Print results with time frame used
                print("r-squared between sample " + str(first_sample_count+1) + " and sample " + str(second_sample_count+1) + ": " + str(r_squared))
                print("with start time of: " + str(data_time_collection[second_sample_count][0]) + " and end time of: " + str(data_time_collection[second_sample_count][-1]) + "\n")

def main():

    csv.field_size_limit(sys.maxsize)

    arg_list = sys.argv[1:]

    display_rsquared_data(arg_list)

if __name__ == '__main__':
    main()
