from Libraries import * 

def generate_masks(image, CheckPointPath):
    """
    Generate masks from an image using a mask generator.

    Args:
    - image: Input image.
    - CheckPointPath: str, Path to the SAM Checkpoint file.

    Returns:
    - masks: List of masks.
    """

    model_type = "vit_l"
    sam = sam_model_registry[model_type](checkpoint=CheckPointPath)
    mask_generator = SamAutomaticMaskGenerator(sam)
    # Generate masks
    masks = mask_generator.generate(np.array(image))
    
    return masks

def filter_parameters(df):
    """
    Filter parameters based on masks information.

    Args:
    - df: pandas.DataFrame, DataFrame containing mask information.

    Returns:
    - min_leaf_areas: list, Minimum leaf areas calculated based on maximum mask areas.
    """
    # Define filtering criteria
    area_max = [max(mask_info['area'] for mask_info in mask_1) for mask_1 in df['Masks']]
    min_leaf_areas = [0.4 * max_area for max_area in area_max]  # Minimum area for a leaf
    return min_leaf_areas

def filter_masks(masks_l, min_leaf_area):
    """
    Filter masks based on area and aspect ratio criteria.

    Args:
    - masks_l: List of masks.
    - min_leaf_area: Minimum area threshold for a leaf.

    Returns:
    - filtered_masks: List of filtered masks.
    - masks_b: List of mask information corresponding to filtered masks.
    """
    max_aspect_ratio = 2.5  # Maximum aspect ratio for a leaf
    filtered_masks = []
    masks_b = []
    for mask_info in masks_l:
        # Get the segmentation mask
        mask = mask_info['segmentation']

        # Compute the area of the segmented region
        area = np.sum(mask)

        # Compute the bounding box of the segmented region
        contours, _ = cv2.findContours(np.uint8(mask), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = cv2.boundingRect(contours[0])

        # Compute the aspect ratio of the bounding box
        aspect_ratio = w / h if h != 0 else 0

        # Check if the mask meets the filtering criteria
        if area > min_leaf_area and aspect_ratio < max_aspect_ratio:
            filtered_masks.append(mask)
            masks_b.append(mask_info)

    return filtered_masks, masks_b


def prepare_test_images(masked_images, img_size=(224, 224), color_mode='rgb'):
    """
    Prepare test images for input to the model from masked image arrays.

    Args:
    - masked_images: List of masked images (arrays).
    - img_size: Tuple specifying the target size of the images (default is (224, 224)).
    - color_mode: Color mode of the images ('rgb' or 'grayscale').

    Returns:
    - test_images_prepared: A numpy array containing the prepared test images.
    """

    # Initialize an empty list to store prepared images
    test_images_prepared = []

    # Preprocess each masked image
    for masked_image in masked_images:


        # Resize the non-black region to fit within a 220x220 dimension
        resized_masked_image = cv2.resize(masked_image, (150, 150))

        # Create a black image of size 224x224
        final_image = np.zeros((224, 224, 3), dtype=np.uint8)

        # Insert the resized non-black region into the black image at an appropriate position
        final_image[37 : 187 , 37 : 187, :] = resized_masked_image

        # Resize the image to the specified size
        img_resized = tf.image.resize(final_image, img_size)

        # Normalize pixel values to [0, 1]
        #img_normalized = img_resized / 255.0
        # Append preprocessed image to the list
        test_images_prepared.append(img_resized)

    # Convert list of images to numpy array
    test_images_prepared = np.array(test_images_prepared)

    return test_images_prepared


def get_masked_leaves(filtered_masks_set, image):
    """
    Process masks and generate test images.

    Args:
    - filtered_masks_set: List of filtered masks.
    - image: Input image.

    Returns:
    - test_images_prepared: A numpy array containing the prepared test images.
    """
    test_images = []

    for mask in filtered_masks_set:
        # Get the bounding box of the non-black region
        non_zero_indices = np.argwhere(mask)

        # Calculate the bounding box coordinates
        min_x = np.min(non_zero_indices[:, 1])
        max_x = np.max(non_zero_indices[:, 1])
        min_y = np.min(non_zero_indices[:, 0])
        max_y = np.max(non_zero_indices[:, 0])

        # Apply the mask to the image
        masked_image = np.copy(image)
        masked_image[~mask] = 0  # Set non-masked regions to black

        # Extract the content within the bounding box defined by the mask
        masked_image = masked_image[min_y:max_y + 1, min_x:max_x + 1]
        test_images.append(masked_image)

    return prepare_test_images(test_images)