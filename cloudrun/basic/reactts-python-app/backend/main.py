import os
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

def create_app():
  app = Flask(__name__)
  CORS(app,  origins="*")
  # Error 404 handler
  @app.errorhandler(404)
  def resource_not_found(e):
    return jsonify(error=str(e)), 404
  # Error 405 handler
  @app.errorhandler(405)
  def resource_not_found(e):
    return jsonify(error=str(e)), 405
  # Error 401 handler
  @app.errorhandler(401)
  def custom_401(error):
    return Response("API Key required.", 401)
  
  @app.route("/ping", methods=['OPTIONS', 'GET'])
  def hello_world():
      if request.method == 'OPTIONS':
          return Response(status=200) #respond to options preflight.
      return "pong"
  
  return app
  
app = create_app()

if __name__ == "__main__":
  print(" Starting app...")
  app.run(host="0.0.0.0", port=5000)