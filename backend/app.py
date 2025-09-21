from flask import Flask

app = Flask(__name__)  # Create a Flask application instance

@app.route("/")  # Define the route URL for the homepage
def hello_world():
    return "<p>Hello, World!</p>"  # Response sent to the browser

if __name__ == "__main__":
    app.run(debug=True)  # Run the app in debug mode for development