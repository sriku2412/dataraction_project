import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

resume = pd.read_csv(r"C:\Users\srika\OneDrive\Documents\York\Sem-2 york\MBAN 6090 - Analytics Consulting Project\webscrape\communitech\resume_data_231230.csv")
jobs = pd.read_csv(r"C:\Users\srika\OneDrive\Documents\York\Sem-2 york\MBAN 6090 - Analytics Consulting Project\webscrape\communitech\jobs_info.csv")


# Clean and prepare the data
resume['Resume'].fillna('', inplace=True)  # Replace NaN with empty strings
jobs['description'].fillna('', inplace=True)  # Replace NaN with empty strings

# Ensure data is in string format
resume['Resume'] = resume['Resume'].astype(str)
jobs['description'] = jobs['description'].astype(str)

# Create TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')

# Combine all texts for TF-IDF
all_texts = pd.concat([resume['Resume'], jobs['description']])
vectorizer.fit(all_texts)

# Transform each resume and job posting
resumes_tfidf = vectorizer.transform(resume['Resume'])
job_postings_tfidf = vectorizer.transform(jobs['description'])

# Calculate cosine similarity
similarity_matrix = cosine_similarity(resumes_tfidf, job_postings_tfidf)

# Process similarity_matrix to find top matches for each resume
# For example, you can loop through each resume and find the top matching job postings

from flask import Flask, request, render_template_string

# Flask app setup
app = Flask(__name__)

# Assuming similarity_matrix, resume, and jobs are defined elsewhere

# Function to find matching jobs
def find_matching_jobs(user_id, page=0, items_per_page=10):
    job_matches = similarity_matrix[user_id]
    # Sort the job matches in descending order of their scores
    sorted_indices = sorted(range(len(job_matches)), key=lambda i: job_matches[i], reverse=True)

    # Calculate the start and end indices for pagination
    start = page * items_per_page
    end = start + items_per_page

    # Select the top matches for the current page
    top_matches_indices = sorted_indices[start:end]
    top_matches_scores = [job_matches[i] for i in top_matches_indices]

    # Normalize scores (optional, depending on your requirement)
    normalized_scores = [round(score / max(top_matches_scores) * 5, 2) if top_matches_scores else 0 for score in top_matches_scores]

    return list(zip(top_matches_indices, normalized_scores))


# Function to display resumes and job matches
def display_resumes_jobs(user_id, page=0):
    html_output = '<h1>Resumes</h1><div style="display:flex;">'

    # Display resume details
    resume_details = resume.iloc[user_id]['Raw_html']
    html_output += f'<div style="flex:1; padding:10px;">{resume_details}</div>'

    # Display job matches
    html_output += '<div style="flex:1; padding:10px;"><ol>'
    matching_jobs = find_matching_jobs(user_id, page)
    for job_id, score in matching_jobs:
        job_title = jobs.iloc[job_id]['title']
        first_line_description = jobs.iloc[job_id]['description'].split('.')[0]
        if len(first_line_description) > 50:  # Limiting length of the description
            first_line_description = first_line_description[:47] + '...'
        html_output += f'<li><a href="/job/{job_id}">{job_title} (Score: {score}/5): {first_line_description}</a></li>'
    html_output += '</ol></div></div>'

    # Pagination
    total_pages = -(-len(similarity_matrix[user_id]) // 10)  # Ceiling division for total pages
   # Update pagination links
    html_output += '<div>Pages: ' + ' '.join([f'<form method="post" style="display:inline;"><input type="hidden" name="resume_id" value="{user_id}"><input type="hidden" name="page" value="{i}"><input type="submit" value="{i+1}"></form>' for i in range(total_pages)]) + '</div>'

    return render_template_string(html_output)

# Route for selecting a resume and displaying job matches
@app.route('/', methods=['GET', 'POST'])
def select_resume():
    if request.method == 'POST':
        user_id = int(request.form['resume_id'])
        page = int(request.form.get('page', 0))
        return display_resumes_jobs(user_id, page)
    else:
        # Create dropdown menu for resume selection
        options = ''.join([f'<option value="{i}">Resume {i}</option>' for i in range(len(resume))])
        return f'''
            <form method="post">
                Select Resume: <select name="resume_id">{options}</select><br>
                <input type="hidden" name="page" value="0">
                <input type="submit" value="Select">
            </form>
        '''

# Route for displaying full job description
@app.route('/job/<int:job_id>')
def job_description_page(job_id):
    job_description = jobs.iloc[job_id]['description']
    return f'<h1>Job Description</h1><p>{job_description}</p>'

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)