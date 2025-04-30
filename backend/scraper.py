from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Replace with your DB URL: postgresql://user:password@localhost/db or mysql+pymysql://...
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'  # Change to PostgreSQL or MySQL in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Job Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    location = db.Column(db.String(100))
    country = db.Column(db.String(100))
    scraped_at = db.Column(db.String(100))

# Create tables
with app.app_context():
    db.create_all()

# Get all jobs
@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    return jsonify([{
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "country": job.country,
        "scraped_at": job.scraped_at
    } for job in jobs])

# Delete job by ID
@app.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        return jsonify({"message": "Job deleted"}), 200
    return jsonify({"error": "Job not found"}), 404

# Optional: Add job manually
@app.route('/jobs', methods=['POST'])
def add_job():
    data = request.json
    new_job = Job(
        title=data['title'],
        company=data['company'],
        location=data['location'],
        country=data['country'],
        scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    db.session.add(new_job)
    db.session.commit()
    return jsonify({"message": "Job added"}), 201

if __name__ == "__main__":
    app.run(debug=True)
