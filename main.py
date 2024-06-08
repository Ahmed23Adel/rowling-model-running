from Libraries import *
from Paths import get_paths
from Drive_authentication import *
from Masks_Generation import *
from Model import *
from Database_Data import *
from Endpoint_data import *

"""
!pip install git+https://github.com/facebookresearch/segment-anything.git
!pip install torch torchvision torchaudio
!pip install pymongo
!pip install schedule
"""

# Directories paths:
CheckPointPath, Credentials_file, model_path, Unchecked_folder_link, Checked_folder_link, \
Resized_folder_id, Annotated_folder_id, connection_string, \
zone_periods_Endpoint, create_image_Endpoint = get_paths()

# Authenticate and get credentials with drive
credentials = authenticate_with_google(Credentials_file)

"""
This part should be checked every 12 hours for example
"""

# Getting the recent added Folder drive data
Recent_Folder_Data = get_recent_folder_link(Unchecked_folder_link, credentials) # [Folder_name, Folder Link, Last modification date]

if Recent_Folder_Data != None: # There is unchecked data

    recent_folder_download_link = Recent_Folder_Data[1]
    recent_folder_date = Recent_Folder_Data[0]
    
    # Getting Drive data
    df = Getting_Images_DataFrame(recent_folder_download_link, recent_folder_date, credentials) # ['Image_Path', 'Image','Location', 'Date', 'time']

    # Generating masks using sam, filter them
    df['Masks'] = df['Image'].apply(lambda x: generate_masks(x, CheckPointPath))

    #Filteration parameters 
    min_leaf_areas = filter_parameters(df)

    # Apply the filtering function to each mask set in df['Masks']
    df['Filtered_Masks'], df['Masks_b'] = zip(*[filter_masks(masks_l, min_leaf_area) for masks_l, min_leaf_area in zip(df['Masks'], min_leaf_areas)])

    # Drop images with non-detected leaves
    df = df[df['Masks_b'].apply(len) > 0]
    # Reset index after filtering
    df.reset_index(drop=True, inplace=True)

    # prepare images for the model
    df['Test_Gen'] = [get_masked_leaves(filtered_masks_set, image) for filtered_masks_set, image in zip(df['Filtered_Masks'], df['Image'])]
    
    # model prediction
    model = load_model(model_path)
    df[['Confidence', 'Classification','Image_Class']] = df['Test_Gen'].apply(lambda x: pd.Series(predict_labels(x, model)))

    # Adding features: bbox, edited, treated (prepare data for the database)
    df[['bbox', 'Edited', 'Treated']] = df['Masks_b'].apply(lambda annotations: pd.Series(add_features(annotations)))

    # Resized Images Path
    df = upload_resized_images_to_drive(df, credentials, Resized_folder_id, Annotated_folder_id)

    
    # Getting data for first endpoint
    Endpoint_1_Data = get_Endpoint_1_data(df)

    # Endpoint1 Call 
    period_Ids = get_Period_ID(Endpoint_1_Data, zone_periods_Endpoint)

    # Update df
    df = add_period_ids(df, Endpoint_1_Data, period_Ids)

    df['Annotated_Path'] = ''
    # Send to mongo 
    Mongo_Cols = ['Image_Path', 'PeriodOfDiseaesId','Classification','Confidence','bbox','Image_Class','Resized_Path','Annotated_Path']

    # Upload Data
    upload_data(df, Mongo_Cols,create_image_Endpoint)

    # Moving the checked data from the processing drive folder to the data_backup folder
    success = move_folder(credentials, recent_folder_download_link, Checked_folder_link)


    