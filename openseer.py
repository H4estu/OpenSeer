import sys
import requests

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import streamlit as st


def query_api(num_sales):
    """Request data from the opensea events API.

    Send a request specifying the last n-number of successful sales 
    recorded on opensea. These data are returned in a human-readable
    format called Javascript Object Notation (JSON), which can then
    be easily turned into tabular data for analysis.

    Check the opensea events API for more details:
    https://docs.opensea.io/reference/retrieving-asset-events

    Parameters
    ----------
    num_sales : int
        The number of sales to request. This is provided as a command-
        line argument to the openseer program.

    Returns
    -------
    response_data : JSON
        A JSON object containing the last-n sales recorded on opensea.
    """
    # The API endpoint containing the recent NFT sales data.
    url = "https://api.opensea.io/api/v1/events"

    response_data = requests.get(
        url,
        params = {
            'event_type': 'successful',  # Request only completed sales
            'limit': num_sales
        }).json()

    # Gracefully exit the program if the API request fails for some
    # reason. Usually reducing the number of sales requested or waiting 
    # a few minutes resolves things.
    if response_data is None:        
        print(
            f'Unable to get data. Try lowering the number of sales requested'
            f' or waiting a few minutes.'
        )
        sys.exit()
    
    return response_data


def parse_data(sales_data):
    """Parse the data from JSON into a a tabular dataframe.

    Tabular (table) data is arranged in a rectangular grid -- it looks 
    like data you would see in an excel spreadsheet. The dataframe will 
    have a number of rows equal to the number of sales requested (n). 
    After the call to parse_data, the sales_data_frame variable will 
    look like the following:
    
    --------------------------------------------- 
    | NFT_Group_Name   | number_of_transactions |
    ---------------------------------------------
    | Collection 1     |            1           |
    | Collection 2     |            1           |     
    |     ...          |           ...          |
    | Collection n     |            1           |
    ---------------------------------------------
    
    Looks like a table, right?

    Parameters
    ----------
    sales_data : JSON 
        A JSON object containing the last-n sales recorded on opensea.
    
    Returns
    -------
    data_frame : pandas.DataFrame
        Tabular data containing two rows: the name of the NFT collection 
        and the number of recent transactions. The number of rows in the
        data frame are equal to n, the number of transactions requested
        from opensea.
    """
    # Establish empty containers (lists, in this case) to store the 
    # collection names and the times of each sale.
    asset_name_list = []
    asset_date_list = []

    # Loop over items in "asset_event" list and get the name of the 
    # collection for each NFT transaction. The name of the collections
    # are saved to asset_name_list, and the date of the transactions
    # are saved to asset_date_list.
    try:
        for item in sales_data['asset_events']:
            asset_name_list.append(item['asset']['collection']['name'])
            asset_date_list.append(item["created_date"])
    except:
        # Again, gracefully exit the program if an error is encountered.
        print(
            f'Unable to parse the data. Try lowering the number of sales' 
            f' requested or waiting a few minutes.'
        )
        sys.exit()

    # Merge lists into a dataframe. Each list is saved as a column in 
    # the data frame.
    data_frame = pd.DataFrame({
        "transaction_date": asset_date_list, 
        "NFT_Group_Name": asset_name_list
        })

    return data_frame


def plot_data(sales_data):
    """Graphically plot the data.

    Create bar plots of the sales data. Each bar represents an NFT 
    collection, and its height represent the number of sales made.

    Parameters
    ----------
    sales_data : pandas.DataFrame
        The sales data in tabular form.
    
    Returns
    -------
    counts : pandas.DataFrame
        The sales data in tabular form, grouped by collection name.
    """
    # Group the sales by NFT collection. Without this, all bars would
    # be of height 1 (i.e. 1 sale), and there would be multiple bars
    # with the same NFT collection name.
    # counts = sales_data.groupby('NFT_Group_Name').count()
    counts = sales_data['NFT_Group_Name'].value_counts()

    # Set the font size of the plot text. If the text is too small, you can
    # increase this number.
    mpl.rc('font', size=7)

    # Establish the plot axes and the size (width, height, in inches) 
    # of the plot window.
    fig, ax = plt.subplots(figsize=(8, 7))

    # Make a bar plot of the data.
    counts.plot.bar(ax=ax)

    # Move the bottom of the plot upward in the window. Without this, 
    # the x-axis labels can get cut off at the bottom of the window. If the
    # NFT collection name is long enough, it still might get cut off. In that
    # case, just manually resize the window by grabbing and mvoing the corner
    # of the plot window.
    plt.subplots_adjust(bottom=0.25)  

    # Increase the x-label font size
    ax.set_xlabel('NFT Collection', fontsize=10)

    # Display the plot to the user. This is what makes the pop-up window!
    # plt.show()

    return counts


def main():
    """
    This is the `main` function, which serves as command-and-control
    for the program. It takes the command-line arguments you passed in
    and routes them to the appropriate functions.
    """

    with st.form('API Parameters'):
        num_sales = st.number_input('Number of sales', min_value=1, max_value=300)
        submitted = st.form_submit_button('Submit')
        
        # Call the function that will request the last-n of sales from opensea
        if submitted:
            sales_data_json = query_api(num_sales)

            # Call the function that will transform the JSON data into a tabular dataframe
            sales_data_frame = parse_data(sales_data_json)

            # Call the function that will plot the sales data grouped by the
            # name of the collection. This line is what gives the bars their 
            # differeing heights in the plot.
            counts = plot_data(sales_data_frame)

            st.header(f'Last {num_sales} Sales by Collection')
            st.bar_chart(counts)

            if num_sales < 3:
                top_selling = num_sales
            else:
                top_selling = 3

            st.subheader(f'Top {top_selling} Collections')
            st.write(counts.iloc[0:top_selling].to_frame('Number of Sales'))

    # Clean up and exit the program!
    return


if __name__ == "__main__":
    main()
