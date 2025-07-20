#!/usr/bin/env python3
"""
Flask application that exposes the LangGraph Map-Reduce functionality.
Provides a REST API endpoint for sum of squares calculation.
"""

import time
from flask import Flask, request, jsonify
from langgraph_mapreduce import run_mapreduce

app = Flask(__name__)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "LangGraph Map-Reduce API",
        "timestamp": time.time()
    })


@app.route('/sum_of_squares', methods=['POST'])
def calculate_sum_of_squares():
    """
    Calculate sum of squares using LangGraph Map-Reduce pattern.
    
    Expected JSON body:
    {
        "length": 100
    }
    
    Returns:
    {
        "sum_of_squares": 123456,
        "length": 100,
        "execution_time": 0.1234,
        "numbers_processed": 100
    }
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400
        
        # Get JSON data
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                "error": "Request body must contain JSON data"
            }), 400
        
        if 'length' not in data:
            return jsonify({
                "error": "Missing required field: 'length'"
            }), 400
        
        # Validate length value
        length = data['length']
        
        if not isinstance(length, int):
            return jsonify({
                "error": "Field 'length' must be an integer"
            }), 400
        
        if length <= 0:
            return jsonify({
                "error": "Field 'length' must be a positive integer"
            }), 400
        
        if length > 10000:  # Reasonable upper limit
            return jsonify({
                "error": "Field 'length' must be <= 10000 for performance reasons"
            }), 400
        
        # Log the request
        print(f"🌐 API Request: POST /sum_of_squares with length={length}")
        
        # Execute the LangGraph map-reduce
        start_time = time.time()
        result = run_mapreduce(length)
        end_time = time.time()
        
        # Prepare response
        response = {
            "sum_of_squares": result["sum_of_squares"],
            "length": result["length"],
            "execution_time": round(result["execution_time"], 4),
            "numbers_processed": result["numbers_processed"],
            "api_response_time": round(end_time - start_time, 4)
        }
        
        print(f"✅ API Response: sum_of_squares={response['sum_of_squares']}")
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/sum_of_squares', methods=['GET'])
def sum_of_squares_info():
    """Provide information about the sum_of_squares endpoint."""
    return jsonify({
        "endpoint": "/sum_of_squares",
        "method": "POST",
        "description": "Calculate sum of squares using LangGraph Map-Reduce",
        "example_request": {
            "length": 100
        },
        "example_response": {
            "sum_of_squares": 123456,
            "length": 100,
            "execution_time": 0.1234,
            "numbers_processed": 100,
            "api_response_time": 0.0056
        },
        "constraints": {
            "length": {
                "type": "integer",
                "min": 1,
                "max": 10000
            }
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "GET /sum_of_squares (info)",
            "POST /sum_of_squares"
        ]
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "error": "Method not allowed for this endpoint",
        "hint": "Try POST /sum_of_squares with JSON body containing 'length'"
    }), 405


if __name__ == '__main__':
    print("🚀 Starting LangGraph Map-Reduce Flask API...")
    print("📊 Available endpoints:")
    print("   GET  /health")
    print("   GET  /sum_of_squares (info)")
    print("   POST /sum_of_squares")
    print("\n🔗 Test with:")
    print("   curl -X POST http://localhost:5000/sum_of_squares \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"length\": 10}'")
    print("\n" + "="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
