from flask import Flask, render_template, request
import pandas as pd
import textdistance
import re
from collections import Counter
import os

app = Flask(__name__)

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the file path relative to the current directory
file_path = os.path.join(current_directory, 'autocorrect_book.txt')

# Open the file with the correct file path
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read from the file
        data = f.read().lower()
        words = re.findall(r'\w+', data)
        words += words
except FileNotFoundError:
    print(f"File '{file_path}' not found.")
    words = []

V = set(words)
words_freq_dict = Counter(words)
Total = sum(words_freq_dict.values())
probs = {}

for k in words_freq_dict.keys():
    probs[k] = words_freq_dict[k] / Total

@app.route('/')
def index():
    return render_template('index.html', suggestions=None)

@app.route('/suggest', methods=['POST'])
def suggest():
    keyword = request.form['keyword'].lower()
    if keyword:
        similarities = [1 - textdistance.Jaccard(qval=2).distance(v, keyword) for v in words_freq_dict.keys()]
        df = pd.DataFrame.from_dict(probs, orient='index').reset_index()
        df.columns = ['Word', 'Prob']
        df['Similarity'] = similarities
        suggestions = df.sort_values(['Similarity', 'Prob'], ascending=False)[['Word', 'Similarity']]
        suggestions_list = suggestions.to_dict('records')  # Convert DataFrame to list of dictionaries
        return render_template('index.html', suggestions=suggestions_list)

if __name__ == '__main__':
    app.run(debug=True)
