import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from functions import * 
import nltk
from nltk.tokenize import word_tokenize
nltk.download('stopwords')


os.makedirs('Articles', exist_ok=True)
os.makedirs('clean_article', exist_ok=True)

# Replace 'input.xlsx' with the actual path to your Excel file
input_file_path = 'Input.xlsx'

# Replace 'extracted_articles' with the desired folder name
Article_output_folder_path = 'Articles'

clean_output_folder_path = 'clean_article'

process_articles(input_file_path, Article_output_folder_path)

specificChar()

stopwordsRemove()

scores = cal_score()

try: 
   scores.to_excel('output.xlsx', index=False)
except:
    import random
    num = random.random()   
    scores.to_excel(f'output{num}.xlsx', index=False)
