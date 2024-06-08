from Libraries import * 

def add_features(annotations):
    """
    Extract bounding box information from annotations.

    Args:
    - annotations: List of dictionaries containing annotation information.

    Returns:
    - bbox_list: List of bounding box information [x1, y1, w, h, x2, y2, w, h, ...] for each detected region.
    - edited: bool, edited or not, default = 0.
    - treated: bool, treated or not, default = 0.
    """

    bbox_list = []
    for annotation in annotations:
        bbox_list.extend(annotation['bbox'])
    edited = 0 
    treated = 0
    return bbox_list, edited, treated



def send_to_mongodb(df, columns_to_send, db_name, collection_name, connection_string):
    """
    Sends selected columns from a DataFrame to a MongoDB database.

    Args:
    - df: DataFrame containing the data.
    - columns_to_send: List of column names to send to MongoDB.
    - db_name: Name of the MongoDB database.
    - collection_name: Name of the MongoDB collection.
    - connection_string: Connection string for MongoDB.

    Returns:
    - None
    """
    # Establish a connection to the MongoDB server using the connection string
    client = pymongo.MongoClient(connection_string)

    # Select the database
    db = client[db_name]

    # Select the collection
    collection = db[collection_name]

    # Convert DataFrame to dictionary with selected columns
    data_to_send = []
    for index, row in df.iterrows():
        record = {}
        for column in columns_to_send:
            value = row[column]
            # Convert NumPy arrays to lists
            if isinstance(value, np.ndarray):
                value = value.tolist()
            record[column] = value
        data_to_send.append(record)

    # Insert data into the collection
    collection.insert_many(data_to_send)


# def send_to_mongodb(df, columns_to_send, db_name, collection_name):
#     """
#     Sends selected columns from a DataFrame to a MongoDB database.

#     Args:
#     - df: DataFrame containing the data.
#     - columns_to_send: List of column names to send to MongoDB.
#     - db_name: Name of the MongoDB database.
#     - collection_name: Name of the MongoDB collection.

#     Returns:
#     - None
#     """

#     # Establish a connection to the MongoDB server (assuming it's running locally)
#     client = pymongo.MongoClient('mongodb://localhost:27017/')

#     # Select the database
#     db = client[db_name]

#     # Select the collection
#     collection = db[collection_name]

#     # Convert DataFrame to dictionary with selected columns
#     # data_to_send = df[columns_to_send].to_dict(orient='records')

#     # Convert DataFrame to dictionary with selected columns
#     data_to_send = []
#     for index, row in df.iterrows():
#         record = {}
#         for column in columns_to_send:
#             value = row[column]
#             # Convert NumPy arrays to lists
#             if isinstance(value, np.ndarray):
#                 value = value.tolist()
#             record[column] = value
#         data_to_send.append(record)

#     # Insert data into the collection
#     collection.insert_many(data_to_send)