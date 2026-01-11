'''A simple health check service that monitors 3 endpoints 
and exposes metrics via /health'''

from flask import Flask, jsonify
import requests
import time


app = Flask(__name__)

#3 endpoints
endpoints = {
    'a': 'https://httpbin.org/status/200',
    'b': 'https://api.github.com',
    'c': 'https://this-does-not-exist-12345.com/fake'}

#metrics for traffic and errors
metrics_storage = {
    'a': {"total_checks": 0, "errors": 0},
    'b': {"total_checks": 0, "errors": 0},
    'c': {"total_checks": 0, "errors": 0}
}

#cheeck status and latency of a given URL
def status(url):
    try:

        begin = time.time()
        response = requests.get(url, timeout=5)
        end = time.time()
        latency = end-begin

        if response.status_code == 200:
            return {"status": "good",
                    "status_code": 200,
                    "latency": round(latency,4)}

        
        return {"status": "down",
                "status_code": response.status_code,
                "latency": latency}
    
    #error handling
    except requests.exceptions.RequestException as e:
        return {
            "status": "down",
            "status_code": None,
            "latency": None,
            "error": str(e)
        }
        


     

@app.route('/health', methods=['GET'])

# Check metrics and status for each endpoint
def health_check():
    results = {}

    for name, url in endpoints.items():
        check_result = status(url)
        
        # Update metrics
        metrics_storage[name]["total_checks"] += 1
        if check_result["status"] != "good":
            metrics_storage[name]["errors"] += 1
        
        check_result["total_traffic"] = metrics_storage[name]["total_checks"]
        check_result["total_errors"] = metrics_storage[name]["errors"]
        # Add metrics to result
    
        results["endpoint_" + name] = check_result
        
    return jsonify({ "health_check_results": results })

if __name__ == '__main__':
    app.run(debug=True)

''' check_result["metrics"] = {
            "total_traffic": metrics_storage[name]["total_checks"],
            "total_errors": metrics_storage[name]["errors"]
        }'''

