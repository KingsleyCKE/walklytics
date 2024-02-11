from flask import Flask, request, render_template, redirect, url_for
from distutils.log import debug 
from fileinput import filename 
import os
from dotenv import load_dotenv
load_dotenv()
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

@app.route("/")
def index():
    return render_template("index.html")

ALLOWED_EXTENSIONS = ['mp4']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_aws(file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)
    try:
        s3.upload_file(file, bucket, s3_file)
        print("success")
        return True
    except FileNotFoundError:
        print("file not found")
        return False
    except NoCredentialsError:
        print("credentials not available")
        return False

@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        f = request.files['video']
        if f and allowed_file(f.filename):
            # Save the file locally
            f.save(f.filename)
            # Assume the upload to S3 is successful for this demo
            video_url = "hackalytics2024gaitanalysis/videos/" + f.filename
            upload_success = upload_to_aws(f.filename, "hackalytics2024gaitanalysis", video_url)
            
            # Simulate processing delay
            #time.sleep(120)  # Simulate time it takes to process the video
            
            # Hardcoded analysis results
            analysis_results = "The user seems to be an amputee, having a prosthetic leg on their left leg. It seems that the user drags that proshetic, so more would have to be put on making sure both legs are even when walking."
            
            # If upload is successful, show the processing message and results
            if upload_success:
                return redirect(url_for('loading', filename=f.filename))
            else:
                return "There was an issue with the video upload."
        else:
            return "Invalid file type."
    return "Invalid request", 400

@app.route('/loading/<filename>')
def loading(filename):
    # Render the loading template, passing the filename to use in the redirect script
    return render_template("loading.html", filename=filename)

@app.route('/results/<filename>')
def show_results(filename):
    # Assuming you have a way to retrieve or generate the results
    analysis_results = "The user seems to be an amputee, having a prosthetic leg on their left leg. It seems that the user drags that prosthetic, so more would have to be put on making sure both legs are even when walking."
    return render_template("submit.html", message="File uploaded successfully", filename=filename, results=analysis_results)

if __name__ == "__main__":
    app.run(debug=True) 