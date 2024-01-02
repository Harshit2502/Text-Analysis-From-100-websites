import os
import re
import zipfile
import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')

def extract_article_text(url):
    try:
        # Send an HTTP request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article text based on the structure of the HTML
            # Customize this based on the actual HTML structure of the articles
            try :
              article_text = soup.find('div', class_='td-post-content tagdiv-type').get_text()
            except:
              article_text = soup.find('div', class_='tdb-block-inner td-fix-index').get_text()


            return article_text

    except Exception as e:
        print(f"Error extracting article from {url}: {e}")

    return None

def process_articles(input_file, output_folder):
  # Read the Excel file into a pandas DataFrame
  df = pd.read_excel(input_file)

  # Create the output folder if it doesn't exist
  #os.makedirs(output_folder, exist_ok=True)

  count = 1
  # Iterate through each row in the DataFrame
  for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    # Extract article text
    article_text = extract_article_text(url)

    # Save the extracted article in a text file within the output folder
    if article_text:
        file_name = f"{url_id}.txt"
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(article_text)
        print(f"Article -{count} from {url} saved to {file_path}")
    count = count+1






def specificChar():

    input_file_path = 'Stopwards.txt'

    # Specify the output text file path
    output_file_path = 'Clean_stopwords.txt'

    # Specify the characters to remove
    remove_characters = ['!', '.', ',', '?', ':', ';', '(', ')', '[', ']', '{', '}', '<', '>', '|', '/', '\\', ' ']

    # Open the input text file in read mode
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        # Read the text from the file
        text = input_file.read()

    # Remove the specified characters from the text
    cleaned_text = re.sub('[' + ''.join(remove_characters) + ']', '', text)

    # Open the output text file in write mode
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write the cleaned text to the file
        output_file.write(cleaned_text)






def stopwordsRemove():
    folder_path = 'Articles'
    result = []

    #get a list of all the text files in the folder
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.txt')]

    #load the english stopwords from nltk
    stopwords_list = stopwords.words('english','Clean_stopwords.txt')

    #iterate over each text file
    for file_path in file_paths:
    #open the file in read mode
        with open(file_path, 'r', encoding='utf-8') as file:
            #read the text from the file
            text = file.read()

        #convert the text to lowercase
        text = text.lower()

        #tokenize the text
        tokens = nltk.word_tokenize(text)

        #remove the stopwords from the tokens
        cleaned_tokens = [token for token in tokens if token not in stopwords_list]

        #reconstruct the text from the cleaned tokens
        cleaned_text = ' '.join(cleaned_tokens)
        result.append(cleaned_text)
    output_folder_clean = 'clean_article'
    i = 0
    for filename in os.listdir('Articles'):
        # Save the processed article in a text file within the output folder
        new_filename =str(filename)
        new_filename = new_filename.split('.')[0]
        file_name = f"{new_filename}clean.txt"
        file_path = os.path.join(output_folder_clean, file_name)
        

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(result[i])

        print(f"Processed article {new_filename} saved to {file_path}")
        i=i+1



def cal_clean_score (text,new_filename):
    with open('MasterDictionary\\negative-words.txt', 'r', encoding='utf-8',errors='ignore') as file:
        n = file.read()
        n_words = word_tokenize(n)

    with open('MasterDictionary\\positive-words.txt', 'r', encoding='utf-8',errors='ignore') as file:
        p = file.read()
        p_words = word_tokenize(p)


    words = word_tokenize(text)

    pronoun_count = personal_pronouns(text)
    
    Total_clean_words =len(words)

    #Positive Score Calculating
    positive_score = sum(1 for word in words if word.lower() in p_words)

    #Negative Score Calculating
    negative_score = sum(-1 for word in words if word.lower() in n_words)
    negative_score = negative_score*-1

    # Polarity
    # range -1 to 1 
    # (Positive Score – Negative Score) / ((Positive Score + Negative Score) + 0.000001)
    nu_p = positive_score - negative_score
    de_p = positive_score + negative_score + 0.000001
    polarity_Score = nu_p / de_p 

    # subjectivity_score
    # range 0 to 1
    # (Positive Score + Negative Score)/ ((Total Words after cleaning) + 0.000001)
    nu_s = positive_score + negative_score
    de_s = Total_clean_words + 0.000001
    subjectivity_score = nu_s / de_s
    
    # sylabus score for each words in a clean article
    Total_sycount = 0

    for word in words : 
        count = syllable_count(word)
        Total_sycount =Total_sycount  +  count

    # No of complex words in a clean article
    complex_word_count = sum(1 for word in words if syllable_count(word) > 2)



    final_score = {'URL_ID':new_filename,'POSITIVE_SCORE':positive_score,'NEGATIVE_SCORE':negative_score,'POLARITY_SCORE':polarity_Score,'SUBJECTIVITY_SCORE':subjectivity_score,'WORD_COUNT' :Total_clean_words,'COMPLEX_WORD_COUNT' :complex_word_count,'SYLLABLE_PER_WORD':Total_sycount,'PERSONAL_PRONOUNS': pronoun_count} 
    
    return final_score

def syllable_count(word):
      # Count the number of vowels in the word
        vowels = "aeiouAEIOU"
        count = sum(1 for char in word if char in vowels)

        # Adjust for common exceptions
        if word.endswith(('es', 'ed')) and count > 1:
            count -= 1

        return count

def personal_pronouns(text):
    
    pronoun_pattern = re.compile(r'\b(?:I|we|my|ours|us)\b', flags=re.IGNORECASE)

    # Find all matches in the text


    matches = pronoun_pattern.findall(text)


    filter_match = [match for match in matches if match != 'US']

    # Count the number of matches
    pronoun_count = len(filter_match)
    return pronoun_count

def clean_score():
    output_folder_clean = 'clean_article'
    result = []

    for filename in os.listdir(output_folder_clean):
        file_path = os.path.join(output_folder_clean, filename)    
        
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

            
            suffix = 'clean'
            new_filename =str(filename)
            new_filename = new_filename.split('.')[0]

            if new_filename.endswith(suffix):
                new_filename = new_filename[:-len(suffix)]


            s = cal_clean_score(text,new_filename)
            #s = {'id':new_filename , 'No_Words' :len(words)}
            result.append(s)
    
    df_clean =pd.DataFrame(result)
    return df_clean

def count_sentences():
    # no of sentences of txt file in articles folder 
    result = []
    #uncleaned articles folder path 
    output_folder_articles = 'Articles'

    for filename in os.listdir(output_folder_articles):
        file_path = os.path.join(output_folder_articles, filename)    
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            # Split the text into sentences using a simple regex pattern
            sentences = re.split(r'[.!?]', text)
            # Remove empty strings from the list (resulting from consecutive sentence-ending punctuation)
            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
            new_filename =str(filename)
            new_filename = new_filename.split('.')[0]

            s = {'URL_ID':new_filename , 'No_sentences' :len(sentences)}
            result.append(s)
    
    df_no_sentence =pd.DataFrame(result)
    return df_no_sentence

def cal_score():
    df_no_sentence = count_sentences()
    df_clean = clean_score()

    df = pd.merge(df_clean,df_no_sentence,on='URL_ID')
    
    df['Avg_Sen_Leng'] = df['WORD_COUNT']/df['No_sentences']
    df['Percentage_complex_word'] = df['COMPLEX_WORD_COUNT']/df['WORD_COUNT']
    df['FOG_INDEX'] = (df['Avg_Sen_Leng']+df['Percentage_complex_word'])*0.4
    input_file_path ='input.xlsx'
    df_i = pd.read_excel(input_file_path)
    df1 = pd.merge(df_i,df,on='URL_ID')    
    
    scores = df1.copy()
    return scores
