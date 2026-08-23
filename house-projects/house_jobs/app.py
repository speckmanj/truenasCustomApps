from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jobs_data.json")


def load_jobs():
    """Load jobs from the JSON data file."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading jobs: {e}")
    return []


def save_jobs(jobs):
    """Save jobs to the JSON data file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(jobs, f, indent=2)
    except Exception as e:
        print(f"Error saving jobs: {e}")


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """Get all jobs."""
    jobs = load_jobs()
    return jsonify(jobs)


@app.route("/api/jobs", methods=["POST"])
def add_job():
    """Add a new job."""
    data = request.get_json()
    job_desc = data.get("job", "").strip()
    
    if not job_desc:
        return jsonify({"error": "Job description is required."}), 400
    
    try:
        price = float(data.get("price", 0))
    except ValueError:
        return jsonify({"error": "Invalid price."}), 400
    
    jobs = load_jobs()
    
    # Generate new ID
    if jobs:
        new_id = max(j["id"] for j in jobs) + 1
    else:
        new_id = 1
    
    # Accept any valid hex color or empty string
    import re
    color = data.get("color", "")
    if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        color = ""
    
    new_job = {
        "id": new_id,
        "job": job_desc,
        "price": price,
        "completed": False,
        "color": color
    }
    
    jobs.append(new_job)
    save_jobs(jobs)
    
    return jsonify(new_job), 201


@app.route("/api/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    """Update a job's description, price, or completed status."""
    data = request.get_json()
    jobs = load_jobs()
    
    import re
    for job in jobs:
        if job["id"] == job_id:
            if "job" in data:
                job["job"] = data["job"].strip()
            if "price" in data:
                try:
                    job["price"] = float(data["price"])
                except ValueError:
                    return jsonify({"error": "Invalid price."}), 400
            if "completed" in data:
                job["completed"] = bool(data["completed"])
            if "color" in data:
                color = data["color"]
                if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                    color = ""
                job["color"] = color
            break
    else:
        return jsonify({"error": "Job not found."}), 404
    
    save_jobs(jobs)
    return jsonify(job)


@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    """Delete a job."""
    jobs = load_jobs()
    
    # Find and remove the job
    new_jobs = [j for j in jobs if j["id"] != job_id]
    
    if len(new_jobs) == len(jobs):
        return jsonify({"error": "Job not found."}), 404
    
    jobs = new_jobs
    
    # Re-number IDs
    for i, job in enumerate(jobs):
        job["id"] = i + 1
    
    save_jobs(jobs)
    return jsonify({"message": "Job deleted."})


if __name__ == "__main__":
    import socket
    # Bind to 0.0.0.0 to allow network access
    app.run(host="0.0.0.0", port=5000, debug=True)
