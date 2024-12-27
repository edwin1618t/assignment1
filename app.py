from flask import Flask, render_template, jsonify, request
import subprocess
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB  
client = MongoClient('mongodb://localhost:27017/') 
db = client['stirx']
collection = db['trending_topics']

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run_script")
def run_script():
    try:
        # Run the Selenium 
        result = subprocess.run(
          ["python", "scraper_script.py"], 
          capture_output=True, 
          text=True,
          encoding='utf-8',   
          errors='ignore'     
             )


        # Log the output for debugging
        print("Script output:", result.stdout)
        print("Script errors:", result.stderr)

        if result.returncode != 0:
            return jsonify({"error": f"Error running script: {result.stderr}"}), 500

        # Fetch the latest  
        latest_record = collection.find().sort([("_id", -1)]).limit(1)

        # Check if any records exist 
        if collection.count_documents({}) == 0:
            return jsonify({"error": "No trends found."}), 404
 
        trend = latest_record[0]

        # Return trend data
        return jsonify({
            "timestamp": trend['timestamp'],
            "trend1": trend['trend1'],
            "trend2": trend['trend2'],
            "trend3": trend['trend3'],
            "trend4": trend['trend4'],
            "ip_address": trend['ip_address']
        })

    except Exception as e:
       
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
 