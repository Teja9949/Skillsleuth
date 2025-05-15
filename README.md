# Skills_Sleuth

A Flask job analytics web application mimicking job search sites like LinkedIn, complete with filtering, sorting, and data visualization. Below is a breakdown of each file in detail.

---

## 1. **app.py** — The Flask Backend

### Responsibilities:
- Loads and preprocesses the dataset (`dice_jobs.csv`)
- Routes all pages: Home, Search, Analytics

### Notable Functions:
- **`/search` route**:
  - Filters by job title, location, and skills
- Sorting by title, location
  - Pagination support
- **`/analytics` route**:
  - Computes top skills, job locations, job posting trends
  - Returns data for frontend charts

---
## 2. **templates/base.html** — Shared HTML Layout

### Responsibilities:
- Provides a common layout and navigation bar across pages
- Provides the loading bar for page transitions

### Contains:
- Navigation menu (Home, Search, Analytics)
- Link to styles.css and Google Fonts
- Full-page loading bar (`#loading-bar`)
- `{% block content %}` and `{% block scripts %}` for page-specific content and scripts

---
## 3. **templates/home.html** — Landing Page

### Responsibilities:
- Provides a welcoming UI with a background image
- Urges users to search for jobs or view analytics

---
## 4. **templates/search.html** — Job Search Page

### Responsibilities:
- Enables users to filter jobs by title, location, and skill
- Sort jobs by title/location/date with ascending/descending order
- Render paginated job results

### Backend Powered By:
- Filters via Flask
- Pagination logic
- Sorting done via `sort_by` and `sort_order`

### Highlights:
- Renders job descriptions, posting date, and formatted skills as tags
- Integrated with Flask to yield search criteria

---

## 5. **templates/analytics.html** — Job Market Analytics Dashboard

### Tasks:
- Displays 4 interactive charts:
  - Top Skills (bar chart)
  - Jobs by City (doughnut chart)
- Job Trends Over Time (line chart)
  - Sentiment by City (bar chart)

### Features:
- Dynamic filtering by city and employment type
- Download button to export all charts as a single image

---
## 6. **static/js/analytics.js** — Chart Control Script

### Responsibilities:
- Renders charts with Chart.js
- Updates charts via AJAX (`fetch`) when filters change
- Dynamically colors bars in sentiment chart by polarity
- Adds `downloadAllChartsAsImage()` to save all charts as one PNG

---
## 7. **static/css/styles.css** — Styles File

### Responsibilities:
- Custom styling for:
  - Navigation bar
  - Job cards
  - Pagination
  - Search form and reset buttons
  - Skill tags
  - Chart containers
  - Responsive design

---
## 8. **data/dice_jobs.csv** — Trained Dataset

### Contents:
- Job title, location, skills, employment type, description

### Usage:
- Preprocessed in `app.py`
- Used for filtering, sorting, and generating analytics

