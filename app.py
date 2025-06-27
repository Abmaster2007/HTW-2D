from Game_backend.routes import create_routes
from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key'

create_routes(app)

if __name__ == '__main__':
    app.run(debug=True)