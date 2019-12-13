from run import app
from flask import jsonify

@app.route("/")
def index():
	return render_template("index.html")
