from Libraries import * 

def map_numbers_to_classes(numbers):
    """
    Map numbers to their corresponding class names for potato.

    Args:
    - numbers: A list of numbers to be mapped.

    Returns:
    - classes: A list of class names corresponding to the input numbers.
    """
    class_mapping = {
        0: 'Early blight',
        1: 'Late blight',
        2: 'Healthy'
    }

    classes = [class_mapping[number] for number in numbers]
    return classes

def predict_labels(test_gen, model):
    """
    Make predictions on the test images using the provided model.

    Args:
    - test_gen: Test data generator.
    - model: Trained model.

    Returns:
    - confidences: List of confidence scores for each prediction.
    - predictions: List of predicted classifications.
    - detected_disease: Image Classification
    """
    preds = model.predict(test_gen)
    predictions = np.argmax(preds, axis=1)
    confidences = np.max(preds, axis=1)

    # Check if class 0 or 1 exists in the predictions
    if 0 in predictions or 1 in predictions:
        # Count occurrences of class 0 and class 1
        counts = np.bincount(predictions)
        # Determine the most frequent class among 0 and 1
        detected_disease = np.argmax(counts[:2])
    else:
        # If only class 2 exists or no predictions, set detected_disease to 2
        detected_disease = 2
    
    return confidences, predictions, detected_disease


def annotate_image(image, bbox_list, confidences, predictions):
    """
    Annotate the input image with bounding boxes and labels based on predictions.

    Args:
    - image: Input image.
    - bbox_list: List of bounding box information [x1, y1, w, h, x2, y2, w, h, ...] for each detected region.
    - confidences: List of confidence scores for each detected region.
    - predictions: List of predicted classifications for each detected region.

    Returns:
    - annotated_image: Annotated image with bounding boxes and labels.
    """
    # Initialize list to store annotated images
    annotated_image = image.copy()
    
    # Iterate over each bounding box and draw on original image
    for i in range(0, len(bbox_list), 4):
        x, y, w, h = bbox_list[i:i+4]
        
        # Get the predicted label and confidence
        label = map_numbers_to_classes([predictions[i // 4]])
        confidence = confidences[i // 4]  # Get the confidence score for the maximum value
        
        # Check if the label is 0 or 1, or if label is 2 and confidence is less than 70%
        if predictions[i // 4] in [0, 1] or (predictions[i // 4] == 2 and confidence < 0.7):
            # Draw bounding box on annotated image
            annotated_image = cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (255, 255, 255), 2)

            # Calculate text position
            text = f"{label}: {confidence * 100:.2f}%"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = x + 5
            text_y = y + text_size[1] + 5  # Adjust vertical position

            # Draw text inside bounding box
            cv2.putText(annotated_image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return annotated_image
