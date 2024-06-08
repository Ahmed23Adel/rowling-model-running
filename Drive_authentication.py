from Libraries import * 
from Model import annotate_image

def authenticate_with_google(credentials_file):
    """
    Authenticates with Google using a service account and returns the credentials object.

    Args:
    - credentials_file: Path to the JSON file containing service account credentials.

    Returns:
    - credentials: Credentials object obtained from the service account key file.
    """
    try:
        # Load service account credentials from file
        credentials = ServiceAccountCredentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])

        return credentials
    except Exception as e:
        print("Error:", e)
        return None


def extract_folder_id(drive_url):
    """
    Extracts the folder ID from the Google Drive folder URL.

    Args:
    - drive_url: URL of the Google Drive folder.

    Returns:
    - folder_id: ID of the Google Drive folder extracted from the URL.
                 Returns None if the URL is invalid or does not contain a folder ID.
    """
    try:
        # Extract the folder ID from the drive URL using regular expressions
        folder_id = re.search(r'/folders/([^/?]+)', drive_url).group(1)
        return folder_id
    except Exception as e:
        print("Failed to extract folder ID:", e)
        return None


def get_recent_folder_link(drive_url, credentials):
    """
    Extracts the most recently updated Google Drive folder's name, download link, and modified date.

    Args:
    - drive_url: URL of the Google Drive folder.
    - credentials: Credentials object obtained from the OAuth 2.0 authorization flow.

    Returns:
    - recent_folder_info: A tuple containing the most recently updated folder's name, download link, and modified date.
                          Returns None if no Google Drive folders are found or if the request fails.
    """
    try:
        # Build the service using the credentials
        service = build('drive', 'v3', credentials=credentials)

        # Extract folder ID from the drive URL
        folder_id = extract_folder_id(drive_url)

        # List subfolders in the folder
        results = service.files().list(q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'", 
                                       fields='files(id, name, modifiedTime, webViewLink)', 
                                       orderBy='name desc').execute()
        subfolders = results.get('files', [])

        # Check if any subfolders were found
        if subfolders:
            # Get details of the most recently updated subfolder
            recent_subfolder = subfolders[0]
            recent_subfolder_name = recent_subfolder['name']
            recent_subfolder_link = recent_subfolder['webViewLink'] + "?usp=drive_link"
            recent_subfolder_modified_date = recent_subfolder['modifiedTime']
            return (recent_subfolder_name, recent_subfolder_link, recent_subfolder_modified_date)
        else:
            print("No subfolders found in the specified folder.")
            return None
    except Exception as e:
        print("Error:", e)
        return None


def Getting_Images_DataFrame(folder_url, date, credentials):
    """
    Extracts image data from the given Google Drive folder URL and returns a DataFrame.

    Args:
    - folder_url: URL of the Google Drive folder containing images.
    - credentials: Credentials object obtained from the OAuth 2.0 authorization flow.
    - date: Date for taking images

    Returns:
    - df: DataFrame containing image paths, images, location, date, and time.
    """
    try:
        # Build the service using the credentials
        service = build('drive', 'v3', credentials=credentials)

        # Extract folder ID from the folder URL
        folder_id = extract_folder_id(folder_url)

        # List files in the folder
        results = service.files().list(q=f"'{folder_id}' in parents", fields='files(id, name, modifiedTime)').execute()
        files = results.get('files', [])

        # Create a list to store image data
        images_data = []
        for file in files:
            image_name = file['name']
            download_link = f"https://drive.google.com/uc?id={file['id']}&export=download"
            path_link = f"https://drive.google.com/file/d/{file['id']}/view?usp=drive_link"
            modified_time = file['modifiedTime']

            # Download the image
            image_response = requests.get(download_link)
            # Check if the image download was successful
            if image_response.status_code == 200:
                # Read the image bytes
                image_bytes = BytesIO(image_response.content)
                
                # Open the image using PIL
                img = Image.open(image_bytes)
                img = np.array(img)
                # Split image name into location and date
                name_parts = image_name.split('_')
                location = "Zone " + name_parts[1]
                time = name_parts[2].split('.')[0]  # Removing the file extension

                # Append image path and image itself to the list
                images_data.append((path_link, img, location, date, time))

        # Create a DataFrame from the list of tuples
        df = pd.DataFrame(images_data, columns=['Image_Path', 'Image', 'Location', 'Date', 'Time'])

        return df
    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()
        

def upload_to_drive(service, image, folder_id, filename):
    """
    Uploads an image to Google Drive and returns its shareable link.
    Appends the current date to the filename to ensure uniqueness.

    Args:
    - service: Drive API service object.
    - image: Image to upload.
    - folder_id: ID of the folder in Google Drive to upload the image to.
    - filename: Name of the file in Google Drive.

    Returns:
    - Shareable link to the uploaded image.
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    unique_filename = f"{filename}_{current_date}.jpg"
    img_byte_arr = cv2.imencode('.jpg', image)[1].tostring()
    media_body = MediaIoBaseUpload(BytesIO(img_byte_arr), mimetype='image/jpeg', resumable=True)
    file_metadata = {'name': unique_filename, 'parents': [folder_id]}
    file = service.files().create(body=file_metadata, media_body=media_body, fields='id').execute()
    file_id = file['id']
    #return f'https://drive.google.com/uc?id={file_id}&export=download'
    return f"https://drive.google.com/file/d/{file_id}/view?usp=drive_link"
    

def upload_resized_images_to_drive(df, credentials, Resized_folder_id, Annotated_folder_id):
    """
    Uploads resized images to Google Drive and returns their shareable links.

    Args:
    - df: DataFrame containing the images and their paths.
    - credentials: Credentials object obtained from the OAuth 2.0 authorization flow.
    - folder_id: ID of the folder in Google Drive to upload the images to.

    Returns:
    - DataFrame with the shareable links to the uploaded images.
    """
    # Build the Drive API service
    service = build('drive', 'v3', credentials=credentials)
    
    # Resize images using lambda function
    df['Resized_Image'] = df['Image'].apply(lambda image: cv2.resize(image, (80, 60)))

    # Upload resized images and store their Drive links
    df['Resized_Path'] = df.apply(lambda row: upload_to_drive(service, row['Resized_Image'], Resized_folder_id, f"resized_image_{row.name}.jpg"), axis=1)
    
    # Use apply along with a lambda function to apply annotate_image to each row
    df['annotated_image'] = df.apply(lambda row: annotate_image(row['Image'], row['bbox'], row['Confidence'], row['Classification']), axis=1)

    
    # In case we want to save the images with their bounding boxes in the drive
    # Upload annotated images and store their Drive links
    #df['Annotated_Path'] = df.apply(lambda row: upload_to_drive(service, row['annotated_image'], Annotated_folder_id, f"annotated_image{row.name}.jpg"), axis=1)
    
    return df


def move_folder(credentials, source_folder_link, target_folder_link):
    """
    Moves a folder from one location to another in Google Drive.

    Args:
    - credentials: Credentials object obtained from the OAuth 2.0 authorization flow.
    - source_folder_link: URL of the folder to be moved.
    - target_folder_link: URL of the target folder where the folder will be moved.

    Returns:
    - True if the folder is successfully moved, False otherwise.
    """
    try:
        # Build the service using the credentials
        service = build('drive', 'v3', credentials=credentials)
        
        # Extract folder IDs from the source and target folder links
        source_folder_id = extract_folder_id(source_folder_link)
        target_folder_id = extract_folder_id(target_folder_link)
        
        # Retrieve metadata of the source folder
        source_folder_metadata = service.files().get(fileId=source_folder_id, fields='parents').execute()
        
        # Remove the source folder from its current parent(s)
        previous_parents = ",".join(source_folder_metadata.get('parents'))
        service.files().update(fileId=source_folder_id, addParents=target_folder_id, removeParents=previous_parents).execute()
        
        return True
    except Exception as e:
        print("Error:", e)
        return False


    