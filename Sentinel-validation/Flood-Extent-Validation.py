import pandas as pd 
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
import os

print(os. getcwd())
os.chdir('/mnt/c/Users/Hannah/Desktop/Centre/pa-bangladesh-aa/')

# Read in the interview data
df = pd.read_excel('Sentinel-1-BGD-Flooding_Flood extent_DATA.xlsx', sheet_name='Sheet1_COPY')

# CHECK: How many NA's are in each row?
# print(len(df) - df.count())

# TODO:
# Test the assumption that there is only 1 start/end date for each tested union - this is incorrect as some unions were flooded more than once
# And that it is always in the first date row  

# Remove entries without any interview data (no values in any of the interview columns)
df_dropped = df.dropna(subset=['Interview_1', 'Interview_2', 'Interview_3'], thresh=1)

# CHECK: How many unique unions are there in the remaining data?
# Should be 20 
# print(df_dropped['ADM4_EN'].nunique())

# Get list of the unique unions that were sampled
sampled_union = df_dropped['ADM4_EN'].unique().tolist()

# Data with standard deviation and mean daily differences
summary = []

sel_union = sampled_union[1]

# Loop through all of the sampled unions 
for sel_union in sampled_union: 

    # Get only the data for the selected union
    df_selected = df_dropped.loc[df_dropped['ADM4_EN'] == sel_union]

    # What is the estimated flood start/end date?
    start = df_selected['flood_start_date1'].iloc[0]
    peak = df_selected['flood_pick_date1'].iloc[0]

    # Get the various estimates of flood extent by date (in %)
    flood_extent = df_selected[['flood_fraction', 'Interview_1','Interview_2', 'Interview_3', 'date']]

    # tranform variables as necessary
    flood_extent['flood_fraction'] = flood_extent['flood_fraction']*100
    flood_extent['date']= pd.to_datetime(flood_extent['date']) 

    # Remove columns with NA values 
    flood_extent = flood_extent.dropna(axis='columns')

    # Melt data to long format for visualization
    flood_extent_long = flood_extent.melt(id_vars=['date'])

    # Colours for the line graph 
    col_mapping = {
        'Interview_1': '#520057',
        'Interview_2': '#db00e8',
        'Interview_3': '#d096d4',
        'flood_fraction': '#ff9626'
    }

    # Create simple line plot to compare the satellite estimates and interviewed estimates
    fig = plt.figure()
    ax = plt.axes()
    sns.lineplot(x='date', y='value', hue='variable', data=flood_extent_long, palette=col_mapping)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Percent flooding estimate')
    plt.title('Estimates of flooding in {}, Bangladesh'.format(sel_union))
    plt.axvline(start, ls='--', color='#0fbd09', label='Flood Start', lw=0.75)
    plt.axvline(peak, ls='--', color='#f20a30', label='Flood Peak', lw=0.75)
    plt.legend(loc='lower right',  bbox_to_anchor=(1.05, 1))
    L=plt.legend()
    L.get_texts()[1].set_text('Sentinel-1')
    L.get_texts()[0].set_text('Legend')
    #handles, labels = ax.get_legend_handles_labels()
    #ax.legend(handles=handles[1:], labels=labels[1:])
    plt.tight_layout()
    plt.savefig("{}.png".format(sel_union))

    # Get columns with interview data
    interview_cols = flood_extent.columns[flood_extent.columns.str.contains('Interview')]

    # Loop through each of these columns 
    for col in interview_cols:
        # Calculate avg and sd daily difference between each interview values and the Sentinel-1 values
        diff_mean = (flood_extent[col] - flood_extent['flood_fraction']).mean()
        diff_sd = (flood_extent[col] - flood_extent['flood_fraction']).std()

        # Add to the output dataframe 
        row = [sel_union, col, diff_mean, diff_sd]
        summary.append(row)

# Create the results dataframe 
summary_df = pd.DataFrame(summary, columns=['Union', 'Interview', 'Mean', 'Sdev'])
summary_df.to_csv('Summary.csv', index=False)


