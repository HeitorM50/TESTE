from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from models.user import User
from models.car import Car
from models.rental import Rental

app = Flask(__name__)
app.secret_key = 'secret_key'

# Dados simulados (banco de dados temporário)
users = []
cars = [
    Car(1, "Fiat Mobi", 2015, "fiat_mobi.jpg", "Prata", 70000, ["Ar-condicionado", "Direção hidráulica"]),
    Car(2, "Chevrolet Prisma", 2019, "chevrolet_prisma.jpg", "Branco", 45000, ["Airbag", "Câmbio automático"]),
    Car(3, "Renault Logan", 2017, "renault_logan.jpg", "Preto", 60000, ["Som Bluetooth", "Vidros elétricos"])
]
rentals = []

# Rota inicial
@app.route('/')
def home():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u.username == username and u.password == password), None)
        if user:
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        flash('Credenciais inválidas!')
    return render_template('login.html')

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users.append(User(username, password))
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
    return render_template('register.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', cars=cars)

# Alugar carro
@app.route('/rent/<int:car_id>', methods=['GET', 'POST'])
def rent_car(car_id):
    car = next((c for c in cars if c.car_id == car_id), None)
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        if start_date > end_date:
            flash("Data de início não pode ser posterior à data de término.")
        else:
            rentals.append(Rental(session['user'], car, start_date, end_date))
            car.available = False
            flash(f"Carro {car.model} alugado de {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}.")
            return redirect(url_for('dashboard'))
    return render_template('rent_car.html', car=car)

@app.route('/availability/<int:car_id>')
def availability(car_id):
    car = next((c for c in cars if c.car_id == car_id), None)
    car_rentals = [r for r in rentals if r.car.car_id == car_id]
    return render_template('car_availability.html', car=car, car_rentals=car_rentals)

@app.route('/description/<int:car_id>')
def description(car_id):
    car = next((c for c in cars if c.car_id == car_id), None)
    return render_template('description.html', car=car)


    



# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)