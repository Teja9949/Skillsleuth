from flask import Flask, jsonify, render_template, request, redirect, url_for
import pandas as pd
import os
from datetime import datetime, timedelta
from textblob import TextBlob
import numpy as np

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pandas')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Loading initial dataset
DATA_PATH = 'data/dice_jobs.csv'
df = pd.read_csv(DATA_PATH)

# Time Conversion ---
def parse_relative_time(text):
    now = datetime.now()
    try:
        text = str(text).lower()
        if 'hour' in text:
            num = int(text.split()[0])
            return now - timedelta(hours=num)
        elif 'minute' in text:
            num = int(text.split()[0])
            return now - timedelta(minutes=num)
        elif 'day' in text:
            num = int(text.split()[0])
            return now - timedelta(days=num)
        elif 'week' in text:
            num = int(text.split()[0])
            return now - timedelta(weeks=num)
        elif 'month' in text:
            num = int(text.split()[0])
            return now - timedelta(weeks=num * 4) 
    except:
        return np.nan
    return np.nan

# Convert postdate to actual datetime
df['postdate'] = df['postdate'].apply(parse_relative_time)
df = df[df['postdate'].notnull()]
df['week'] = df['postdate'].dt.to_period('W').astype(str)

df['sentiment'] = df['jobdescription'].fillna('').apply(lambda x: TextBlob(x).sentiment.polarity)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    title_filter = request.args.get('title', '').lower()
    location_filter = request.args.get('location', '').lower()
    skill_filter = request.args.get('skill', '').lower()
    sort_by = request.args.get('sort_by', '')
    sort_order = request.args.get('sort_order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = 10
    ascending = sort_order == 'asc'

    filtered_df = df.copy()

    if 'postdate' in filtered_df.columns:
        filtered_df['postdate'] = pd.to_datetime(filtered_df['postdate'], errors='coerce')

    # Apply sorting before filtering to maintain order
    if sort_by == 'title':
        filtered_df = filtered_df.sort_values(by='jobtitle', ascending=ascending, na_position='last')
    elif sort_by == 'location':
        filtered_df = filtered_df.sort_values(by='joblocation_address', ascending=ascending, na_position='last')
    elif sort_by == 'date':
        filtered_df = filtered_df.sort_values(by='postdate', ascending=ascending, na_position='last')
    else:
        if 'postdate' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by='postdate', ascending=False, na_position='last')

    # Filtering (after sorting)
    if title_filter:
        filtered_df = filtered_df[filtered_df['jobtitle'].str.lower().str.contains(title_filter, na=False)]
    if location_filter:
        filtered_df = filtered_df[filtered_df['joblocation_address'].str.lower().str.contains(location_filter, na=False)]
    if skill_filter:
        filtered_df = filtered_df[filtered_df['skills'].str.lower().str.contains(skill_filter, na=False)]

    total_jobs = len(filtered_df)
    total_pages = (total_jobs + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    jobs = filtered_df.iloc[start:end].to_dict(orient='records')
    page_range = range(max(1, page - 2), min(total_pages + 1, page + 3))

    return render_template(
        'search.html',
        jobs=jobs,
        count=total_jobs,
        page=page,
        total_pages=total_pages,
        page_range=page_range,
        title=title_filter,
        location=location_filter,
        skill=skill_filter,
        sort_by=sort_by,
        sort_order=sort_order
    )

@app.route('/analytics')
def analytics():
    cities = df['joblocation_address'].dropna().str.extract(r'(.*),')[0].dropna().unique().tolist()
    etypes = df['employmenttype_jobstatus'].dropna().unique().tolist()
    etypes = sorted({etype.strip() for etype in etypes if etype.strip() != ''})

    top_skills = df['skills'].dropna().str.split(', ').explode().value_counts().head(10).to_dict()
    jobs_by_city = df['joblocation_address'].dropna().str.extract(r'(.*),')[0].value_counts().head(5).to_dict()
    jobs_by_week = df.groupby('week').size().to_dict()
    sentiment_by_city = df.groupby(df['joblocation_address'].str.extract(r'(.*),')[0])['sentiment'].mean().dropna().to_dict()

    return render_template(
        'analytics.html',
        top_skills=top_skills,
        jobs_by_city=jobs_by_city,
        all_cities=sorted(cities),
        employment_types=etypes,
        jobs_by_week=jobs_by_week,
        sentiment_by_city=sentiment_by_city
    )


@app.route('/analytics/data')
def analytics_data():
    city = request.args.get('city', '')
    etype = request.args.get('type', '')

    filtered = df.copy()    
    if city:
        filtered = filtered[filtered['joblocation_address'].str.extract(r'(.*),')[0].str.strip().str.lower() == city.lower()]
    if etype:
        filtered = filtered[filtered['employmenttype_jobstatus'].str.contains(fr'\b{etype}\b', case=False, na=False)]

    # Top 10 skills
    top_skills = (
        filtered['skills'].dropna().str.split(', ')
        .explode().value_counts().head(10).to_dict()
    )

    # Top 5 cities
    cities = (
        filtered['joblocation_address'].dropna().str.extract(r'(.*),')[0]
        .value_counts().head(5).to_dict()
    )

    # Weekly job trend
    filtered['postdate'] = pd.to_datetime(filtered['postdate'], errors='coerce')
    filtered = filtered.dropna(subset=['postdate'])
    filtered['week'] = filtered['postdate'].dt.to_period('W').astype(str)
    jobs_by_week = filtered.groupby('week').size().to_dict()

    # Sentiment by city
    from textblob import TextBlob
    filtered['sentiment'] = filtered['jobdescription'].fillna('').apply(lambda x: TextBlob(x).sentiment.polarity)
    sentiment_by_city = (
        filtered.groupby(filtered['joblocation_address'].str.extract(r'(.*),')[0])
        ['sentiment'].mean().dropna().to_dict()
    )

    return jsonify({
        'top_skills': top_skills,
        'jobs_by_city': cities,
        'jobs_by_week': jobs_by_week,
        'sentiment_by_city': sentiment_by_city
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)