from flask import Flask, render_template, request
import psycopg2, psycopg2.extras

app = Flask(__name__)

def get_connection(params):
    return psycopg2.connect(**params, cursor_factory=psycopg2.extras.DictCursor)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        params = {
            'host': request.form['host'],
            'port': request.form['port'],
            'dbname': request.form['dbname'],
            'user': request.form['user'],
            'password': request.form['password']
        }
        try:
            with get_connection(params) as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT nombre, precio, cantidad FROM productos')
                    productos = cur.fetchall()
            return render_template('tabla.html', productos=productos)
        except Exception as e:
            return f"<h3>Error: {e}</h3>"
    return render_template('form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
