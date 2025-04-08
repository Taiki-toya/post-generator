from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_script():
    # post_generator.py を実行
    subprocess.run(["python3", "post_generator.py"])
    return {"status": "success"}