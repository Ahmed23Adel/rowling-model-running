# Rowling: Plant Disease Detection System

## Overview
Rowling is a plant disease detection and monitoring system designed for agricultural fields. It processes images captured from fields, identifies diseased zones, and provides real-time insights for crop management.

## Features
- Image processing and segmentation using SAM (Segment Anything).
- Disease classification with deep learning models.
- Real-time monitoring and data storage with MongoDB.
- User-friendly web interface for visualization.

## Installation
1. Install required libraries with provided `pip install` commands.
2. Configure directory paths and authentication settings.
3. Ensure connectivity to Google Drive and MongoDB.
4. Run the main script for image processing and detection.

## Usage
- Upload field images to designated Google Drive folder.
- Rowling automatically detects diseases and updates results in the database.
- Access web interface to visualize results and monitor crop health.

## Directory Structure
- `Libraries/`: Custom Python modules for image processing and classification.
- `Models/`: Trained deep learning models.
- `Data/`: Configuration files and authentication tokens.

## Credits
- SAM for segmentation.
- TensorFlow, Keras, OpenCV for development.
- Google Drive API, PyDrive for cloud storage.
- MongoDB for data management.

## License
This project is licensed under the MIT License.


Model weights:

https://drive.google.com/file/d/1P7fhkPXlTGnNXQIeLouVaH4Tm7z5_jkO/view?usp=sharing

