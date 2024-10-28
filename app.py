from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

# Function to find positions (same as before)
def find_positions(text, start):
    row = text.count('\n', 0, start) + 1
    last_newline = text.rfind('\n', 0, start)
    col = start - last_newline
    return (row, col)

# Brute Force Search Function (same as before)
def brute_force_search(text, pattern, whole_word):
    start_time = time.time()
    matches = []
    for i in range(len(text) - len(pattern) + 1):
        match_found = True
        for j in range(len(pattern)):
            if text[i + j] != pattern[j]:
                match_found = False
                break
        if match_found:
            if whole_word:
                if (i == 0 or not text[i-1].isalnum()) and ((i + len(pattern) == len(text)) or not text[i + len(pattern)].isalnum()):
                    row, col = find_positions(text, i)
                    matches.append((text[i:i + len(pattern)], row, col))
            else:
                start, end = i, i + len(pattern)
                while start > 0 and text[start - 1].isalnum():
                    start -= 1
                while end < len(text) and text[end].isalnum():
                    end += 1
                row, col = find_positions(text, start)
                matches.append((text[start:end], row, col))
    time_taken = time.time() - start_time
    return matches, time_taken

# KMP Search Function (same as before)
def kmp_search(text, pattern, whole_word):
    start_time = time.time()
    lps = [0] * len(pattern)
    length = 0
    i = 1
    matches = []

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    i = 0
    j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            start = i - j
            if whole_word:
                if (start == 0 or not text[start - 1].isalnum()) and ((start + j == len(text)) or not text[start + j].isalnum()):
                    row, col = find_positions(text, start)
                    matches.append((text[start:start + j], row, col))
            else:
                end = start + j
                while start > 0 and text[start - 1].isalnum():
                    start -= 1
                while end < len(text) and text[end].isalnum():
                    end += 1
                row, col = find_positions(text, start)
                matches.append((text[start:end], row, col))
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    time_taken = time.time() - start_time
    return matches, time_taken

# Search Files Function (same as before, but with adjustments for Flask)
def search_files(search_term, folder_path, case_sensitive, whole_word):
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    results = []

    for file in files:
        with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
            text = f.read()
            if not case_sensitive:
                text = text.lower()
                search_term = search_term.lower()

            matches, brute_time = brute_force_search(text, search_term, whole_word)
            more_matches, kmp_time = kmp_search(text, search_term, whole_word)
            matches += more_matches

            if matches:
                results.append({
                    'file': file,
                    'matches': matches,
                    'brute_time': brute_time,
                    'kmp_time': kmp_time
                })

    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form['search_term']
        case_sensitive = 'case_sensitive' in request.form
        whole_word = 'whole_word' in request.form
        folder_path = r"C:\Users\HP\OneDrive\Desktop\templates"  # Update your folder path

        if not search_term:
            flash('Please enter a search term.')
            return redirect(url_for('index'))

        results = search_files(search_term, folder_path, case_sensitive, whole_word)
        return render_template('index.html', results=results, search_term=search_term)

    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
