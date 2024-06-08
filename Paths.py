import os

def get_paths(current_directory = os.getcwd()):
    """
    Construct paths for various files.

    Args:
    - current_directory: String, path to the current directory.

    Returns:
    - CheckPointPath: String, path to the SAM Checkpoint file.
    - Credentials_file: String, path to the authentication credentials file.
    - model_path: String, path to the classification model file.
    """
    # SAM CheckPoint Path
    CheckPointname = "sam_vit_l_0b3195.pth"
    CheckPointPath = os.path.join(current_directory, CheckPointname)

    # Service account json file path
    credentials_file_name = "model-union-418902-944eade71c87.json"
    Credentials_file = os.path.join(current_directory, credentials_file_name)

    # Classification model
    model_name = "efficientnetb3-Plant Village&Doc Disease-Potato-94.57.h5"
    Model_path = os.path.join(current_directory, model_name)

    # Drive folder link
    Unchecked_folder_link = "https://drive.google.com/drive/folders/1w8Y2YonL3nCC6tOIs1oTEiOAEH8CSGoE?usp=drive_link"

    # Checked Folder Link
    Checked_folder_link = "https://drive.google.com/drive/folders/1IVS74vSjbu6DmaEUH_sSEBi3W6NHZauz?usp=drive_link"

    # Resized Folder id
    Resized_folder_id = '1Y5mubq6e0UKZZehWXnxHkJGvLaBc6LCX'

    # Annotated Folder id
    Annotated_folder_id = '1j7v8rmxdBG9wj5Bk2q81opymItagzoqM'

    # Database Connection 
    connection_string = 'mongodb+srv://ahmedadelabdelmohsn:qU21j4dZ09wbN248@rowling.3olyeve.mongodb.net/myDatabase?retryWrites=true&w=majority&tls=true'

    # Endpoint1
    zone_periods_Endpoint_link = "http://rowling-backend3.eastus.azurecontainer.io:8000/api/v1/handle_zones_periods_of_disease"

    # Endpoint2
    create_image_Endpoint_link = "http://rowling-backend3.eastus.azurecontainer.io:8000/api/v1/create_image"
    
    return CheckPointPath, Credentials_file, Model_path, Unchecked_folder_link, Checked_folder_link, Resized_folder_id, Annotated_folder_id, connection_string, zone_periods_Endpoint_link, create_image_Endpoint_link