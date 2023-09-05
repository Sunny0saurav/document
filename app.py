import boto3
import os

import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import boto3

app = Flask(__name__)

AWS_ACCESS_KEY_ID = 'AKIAUFFETLAR2FOPUO62'
AWS_SECRET_ACCESS_KEY = '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'
S3_BUCKET_NAME = 'app-awsa'


s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

UPLOAD_FOLDER = '/home'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        filename = request.form['filename']
        file = request.files['file']

        if not email or not filename or not file:
            return "Email, Filename, and File are mandatory fields."

        file_key = f'{email}_{filename}'

        s3.upload_fileobj(file, S3_BUCKET_NAME, file_key)

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    email = request.form['email']
    search_query = request.form['search_query']

    if not email:
        return "Email is a mandatory field."

 
    objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)

    results = []

    for obj in objects.get('Contents', []):
        if email in obj['Key'] and search_query in obj['Key']:
            results.append(obj['Key'])

    return render_template('search.html', email=email, search_query=search_query, results=results)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        s3.download_file(S3_BUCKET_NAME, filename, os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return str(e)
