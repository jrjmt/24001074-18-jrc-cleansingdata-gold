# Flask
from flask import Flask, jsonify, redirect, request

# Regex
import re

# Pandas
import pandas as pd

# Encode & decode lib
import base64

# SQLite3
import sqlite3

# Operation System
import os

# Konversikan kedalam bytes.
import io

#import web browser
import webbrowser

# Fungsi Cleansing Data
def normalize_alay(twitter_tweets):
    path_kamus_alay = '/home/jrjmt/Github_Cleansingdata/24001074-18-jrc-cleansingdata-gold/Challenge_Gold/docs/new_kamusalay.csv'
    df_kamus_alay = pd.read_csv(path_kamus_alay, encoding='iso-8859-1')
    
    #iloc = Index location
    #mengambil data pada kolom tertentu dan baris tertentu saja dari keseluruhan data
    alay_dict_map = dict(zip(df_kamus_alay.iloc[:, 0], df_kamus_alay.iloc[:, 1]))
    alay_dict_map
    return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in twitter_tweets.split(' ')])

# Definisikan Clean Text
def clean_text (twitter_tweets):
    
    twitter_tweets = re.sub('USER','',twitter_tweets)
    twitter_tweets = re.sub('RT','',twitter_tweets)
    twitter_tweets = re.sub('http\S+', '', twitter_tweets)
    twitter_tweets = re.sub(r'[^a-zA-Z0-9]', ' ', twitter_tweets)
    twitter_tweets = re.sub(r'x[a-f0-9a-fA-F]{2}', '', twitter_tweets)
    twitter_tweets = re.sub(r'\b\w\b','', twitter_tweets)
    twitter_tweets = re.sub(r'\s+', ' ', twitter_tweets)
    twitter_tweets = re.sub(r'^\d+\s*', '', twitter_tweets)
    twitter_tweets = re.sub(r'[^\x08-\x7f]',r'',twitter_tweets)
    twitter_tweets = re.sub('\?','',twitter_tweets)
    twitter_tweets = re.sub('/na','',twitter_tweets)
    twitter_tweets = re.sub(r'www\.[^ ]+', '',twitter_tweets)
    twitter_tweets = twitter_tweets.strip()
    twitter_tweets = twitter_tweets.lower()
    
    return twitter_tweets

# Swagger
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

# Flask kredensial
app = Flask(__name__)

# Untuk mengarahkan langsung ke Website Swagger UI
@app.route('/')
def index():
    return redirect('/docs')

def open_browser():
    webbrowser.open('http://localhost:5000/docs')
    
# Swagger
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Challenge Gold "API"'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Input Form + Cleansing Data'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)

###body API
#Dimatikan karena sudah auto direct ke Website Swagger UI (Baris 65 - 70)
#@app.route('/', methods=['GET'])
#def hello_world():
#    json_response = {
#        'data': "Hello World"
#    }
#    return jsonify(json_response)

# Body API
@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/input_teks', methods=['POST'])
def input_teks():
    data = request.form.get('text')
    data_umur = request.form.get('umur')
    data_uper = clean_text(data)

    json_response = {
        'output': data_uper,
        'umur': data_umur
    }

    return jsonify(json_response)

#input CSV
@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():
    
    # io.BytesIO = Konversikan kedalam bytes menggunakan ISO-8859-1.
    file = request.files['file']
    contents = file.read()
    df = pd.read_csv(io.BytesIO(contents), encoding='ISO-8859-1')
    
    # Definsikan Keluaran Direktori dan File Path
    output_directory = '/home/jrjmt/Github_Cleansingdata/24001074-18-jrc-cleansingdata-gold/Challenge_Gold/docs/Result_Data'
    output_file_path = os.path.join(output_directory, 'data_mentah_tweet.csv')
    
    # Simpan Dataframe ke Format .CSV 
    df.to_csv(output_file_path, index=False)
    
    # Setup Path
    Path_file = '/home/jrjmt/Github_Cleansingdata/24001074-18-jrc-cleansingdata-gold/Challenge_Gold/docs/Result_Data/data_mentah_tweet.csv'
    
    data_tweets = pd.read_csv(Path_file, encoding='ISO-8859-1')
    
    # Konversikan Data Frame ke SQL
    conn = sqlite3.connect ('challenge_data_tweet')
    data_tweets.to_sql('data_tweets', conn, if_exists='append', index = False)
    
    # Cleansing
    data_tweets['cleansing_tweets'] = data_tweets['Tweet'].apply(clean_text)
    
    # Membersihkan kata-kata alay dengan new_kamus_alay
    data_tweets['cleansing_tweets'] = data_tweets['cleansing_tweets'].apply(normalize_alay)
    
    data_tweets['cleansing_tweets'] = data_tweets['cleansing_tweets'].apply(lambda x: x.lower() if isinstance(x, str) else x)
    
    # Konversikan cleansing data ke Format .CSV 
    cleansed_file_path = os.path.join(output_directory, 'hasil_cleansing_tweet.csv')
    data_tweets.to_csv(cleansed_file_path, index=False)
    
    # Menampilkan hasil cleansing data ke API
    result_cleansing_dataraw = data_tweets['cleansing_tweets'].tolist()
    
    # Response Json  
    json_response = {
        'output': result_cleansing_dataraw,
    }
    return jsonify(json_response)
    
# Jalankan API
if __name__ == '__main__':
    app.run()