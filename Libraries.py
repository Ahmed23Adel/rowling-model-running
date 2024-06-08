import matplotlib.pyplot as plt
import cv2
import os
import io
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload  
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PIL import Image
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
import re
import pymongo
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import json
import datetime
#import schedule
from collections import Counter
