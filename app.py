from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

def load_entries():
    if not os.path.exists('entries.json'):
        return []
    with open('entries.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_entries(entries):
    with open('entries.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

entries = load_entries()

@app.route('/')
def index():
    return render_template('index.html', entries=entries)

@app.route('/entry/<int:entry_id>')
def detail(entry_id):
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if entry:
        return render_template('detail.html', entry=entry)
    return "Запись не найдена", 404

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_id = max([e['id'] for e in entries]) + 1 if entries else 1
        entry = {
            'id': new_id,
            'title': title,
            'content': content,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        entries.append(entry)
        save_entries(entries)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if not entry:
        return "Запись не найдена", 404
    if request.method == 'POST':
        entry['title'] = request.form.get('title')
        entry['content'] = request.form.get('content')
        save_entries(entries)
        return redirect(url_for('index'))
    return render_template('edit.html', entry=entry)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    global entries
    entries = [e for e in entries if e['id'] != entry_id]
    save_entries(entries)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    filtered_entries = [e for e in entries if query in e['title'].lower()]
    return render_template('index.html', entries=filtered_entries)

@app.route('/filter/week')
def filter_week():
    week_ago = datetime.now() - timedelta(days=7)
    filtered_entries = []
    for e in entries:
        entry_date = datetime.strptime(e['date'], '%Y-%m-%d %H:%M:%S')
        if entry_date >= week_ago:
            filtered_entries.append(e)
    return render_template('index.html', entries=filtered_entries)

if __name__ == '__main__':
    app.run(debug=True)
