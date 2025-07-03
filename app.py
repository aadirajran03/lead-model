from flask import Flask, render_template, request, redirect, url_for
from ai_scoring import calculate_score
from collections import Counter
import json

app = Flask(__name__)
leads = []

@app.route('/')
def dashboard():
    category_counts = dict(Counter([lead['category'] for lead in leads]))
    scores_by_category = {}
    for lead in leads:
        scores_by_category.setdefault(lead['category'], []).append(lead['score'])
    avg_scores = {cat: round(sum(vals)/len(vals), 2) for cat, vals in scores_by_category.items()}
    return render_template('dashboard.html', leads=leads, category_counts=json.dumps(category_counts), avg_scores=json.dumps(avg_scores))

@app.route('/add', methods=['GET', 'POST'])
def add_lead():
    if request.method == 'POST':
        data = request.form
        score = calculate_score(data['category'], data['priority'])
        lead = {
            'name': data['name'],
            'email': data['email'],
            'category': data['category'],
            'priority': data['priority'],
            'score': score,
            'next_follow_up': data.get('next_follow_up', '')
        }
        leads.append(lead)
        return redirect(url_for('dashboard'))
    return render_template('add_lead.html')

if __name__ == '__main__':
    app.run(debug=True)
