from Libraries import * 
from Model import map_numbers_to_classes
def get_Endpoint_1_data(df):
    """
    Processes the input DataFrame to determine the majority vote for 'Image_Class' by 'Location' and maps
    these to their corresponding class names.

    Args:
    - df: A pandas DataFrame containing the data to be processed.

    Returns:
    - A dictionary with the zone names and their current disease class.
    """
    # Group by 'Location' and determine the majority vote for 'Image_Class'
    majority_class_per_location = df.groupby('Location')['Image_Class'].agg(lambda x: Counter(x).most_common(1)[0][0])
    
    # Convert the majority class numbers to their corresponding class names
    majority_class_names = map_numbers_to_classes(majority_class_per_location.tolist())
    
    # Construct the output
    output = {
        "zones": [
            {
                "zone_name": f"{location}",
                "current_disease": disease
            }
            for location, disease in zip(majority_class_per_location.index, majority_class_names)
        ]
    }
    
    return output


def get_Period_ID(file, zone_periods_Endpoint_link):
    """
    Sends a POST request to retrieve period IDs for the given file.

    Args:
    - file: The file content to be sent in the request body.
    - zone_periods_Endpoint_link: URL of the endpoint to which the POST request is sent.

    Returns:
    - A list of period IDs extracted from the response.
    """
    res = requests.post(
        zone_periods_Endpoint_link,
        json=file,
    )
    data =json.loads(res.content)
    return(data['data']['periodIds'])


def add_period_ids(df, zones_output, ids):
    """
    Adds period IDs to the DataFrame based on zone names and their corresponding period IDs.

    Args:
    - df: A pandas DataFrame containing the data.
    - zones_output: A dictionary containing zone names and their current disease classes.
    - ids: A list of period IDs to be mapped to the DataFrame.

    Returns:
    - The DataFrame with added 'PeriodOfDiseaesId' column.
    """
    # Create a mapping from zone names to IDs
    zone_to_id_mapping = {
        zone['zone_name']: period_id
        for zone, period_id in zip(zones_output['zones'], ids)
    }
    
    # Extract the zone number from the 'zone_name' for easier comparison with 'Location'
    def extract_zone_number(zone_name):
        return zone_name.split()[1]
    
    # Adjust the zone_to_id_mapping to use the zone numbers as keys
    zone_to_id_mapping = {
        extract_zone_number(zone_name): period_id
        for zone_name, period_id in zone_to_id_mapping.items()
    }
    
    # Extract the zone number from the 'Location' column
    df['LocationNumber'] = df['Location'].apply(extract_zone_number)
    
    # Map the Period_Id to the DataFrame based on the Location
    df['PeriodOfDiseaesId'] = df['LocationNumber'].map(zone_to_id_mapping)
    
    # Drop the temporary 'LocationNumber' column
    df.drop(columns=['LocationNumber'], inplace=True)
    
    return df


def upload_data(df, columns, url):
    """
    Uploads data from the DataFrame to the specified URL by sending a POST request for each row.

    Args:
    - df: A pandas DataFrame containing the data to be uploaded.
    - columns: A list of column names to be included in the payload.
    - url: The endpoint URL to which the POST request will be sent to create image.

    Returns:
    - None
    """
    
    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        # Create a dictionary with the specified columns
        row_data = {col: row[col] for col in columns}
        
        # Convert numpy arrays to lists
        for key, value in row_data.items():
            if isinstance(value, np.ndarray):
                row_data[key] = value.tolist()
        
        
        # Send the dictionary as a JSON payload in a POST request
        try:
            headers = {'Content-Type': 'application/json'}
            res = requests.post(url, json=row_data, headers=headers)
            res.raise_for_status()  # Raise an exception for HTTP errors
            data = res.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {res.content}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request exception occurred: {req_err}")
        except ValueError as val_err:
            print(f"Value error occurred: {val_err}")
