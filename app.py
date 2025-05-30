from flask import Flask, app,request,jsonify,render_template,send_from_directory
from flask import jsonify

@app.route("/api/data")
def get_data():
    try:
        data = {"key": "value"}
        return jsonify({"status": "success", "data": data})  
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

