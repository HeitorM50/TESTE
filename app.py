from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from models.user import Customer, Admin
from models.car import Car
from models.rental import Rental

app = Flask(__name__)
app.secret_key = 'secret_key'

# Dados simulados (banco de dados temporário)
users = {
    'admin': Admin('admin', 'adminpass'),
}
cars = [
    Car(car_id=1, model="Fiat Mobi", year=2015, image="fiat_mobi.jpg", color="Prata", mileage=70000, accessories=["Ar-condicionado", "Direção hidráulica"]),
    Car(car_id=2, model="Chevrolet Prisma", year=2019, image="chevrolet_prisma.jpg", color="Branco", mileage=45000, accessories=["Airbag", "Câmbio automático"]),
    Car(car_id=3, model="Renault Logan", year=2017, image="renault_logan.jpg", color="Preto", mileage=60000, accessories=["Som Bluetooth", "Vidros elétricos"])
]
rentals = []

def is_car_available(car_id, start_date, end_date):
    for rental in rentals:
        if rental.car.car_id == car_id:
            # Se as datas se sobrepõem, o carro não está disponível
            if not (end_date < rental.start_date or start_date > rental.end_date):
                return False
    return True

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
        user = users.get(username)
        if user and user.password == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('Credenciais inválidas!')
    return render_template('login.html')

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Nome de usuário já existe!')
        else:
            users[username] = Customer(username, password)
            flash('Cadastro realizado com sucesso!')
            return redirect(url_for('login'))
    return render_template('register.html')

# Dashboard com polimorfismo
@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    user = users.get(username)
    if not user:
        return redirect(url_for('login'))

    # Atualiza a disponibilidade: se a data final do aluguel já passou, o carro fica disponível novamente
    for rental in rentals:
        if rental.end_date < datetime.now():
            rental.car.is_available = True

    if isinstance(user, Admin):
        return render_template('admin_dashboard.html', cars=cars)
    else:
        user_rentals = [r for r in rentals if r.user == username]
        return render_template('dashboard.html', cars=cars, user_rentals=user_rentals, rentals=rentals)

# Alugar carro
@app.route('/rent/<int:car_id>', methods=['GET', 'POST'])
def rent_car(car_id):
    car = next((c for c in cars if c.car_id == car_id), None)
    if not car:
        flash("Carro não encontrado.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        except ValueError:
            flash("Formato de data inválido.")
            return redirect(url_for('rent_car', car_id=car_id))

        if start_date > end_date:
            flash("Data de início não pode ser posterior à data de término.")
        elif not is_car_available(car_id, start_date, end_date):
            flash("Este carro já está alugado nesse período.")
        else:
            rental = Rental(user=session['username'], car=car, start_date=start_date, end_date=end_date)
            rentals.append(rental)

            # Verifica se existe algum aluguel atual ou futuro para definir a disponibilidade
            car.is_available = not any(r.car.car_id == car_id and r.end_date >= datetime.now() for r in rentals)

            flash(f"Carro {car.model} alugado de {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
            return redirect(url_for('dashboard'))

    return render_template('rent_car.html', car=car)

# Disponibilidade do carro
@app.route('/availability/<int:car_id>')
def availability(car_id):
    car = next((c for c in cars if c.car_id == car_id), None)
    if not car:
        flash("Carro não encontrado.")
        return redirect(url_for('dashboard'))

    car_rentals = [r for r in rentals if r.car.car_id == car_id]
    return render_template('car_availability.html', car=car, rentals=car_rentals)

# Descrição do carro
@app.route('/description/<int:car_id>')
def description(car_id):
    car = next((c for c in cars if c.car_id == car_id), None)
    if not car:
        flash("Carro não encontrado.")
        return redirect(url_for('dashboard'))

    return render_template('description.html', car=car)

# Funções administrativas
@app.route('/admin/add_car', methods=['GET', 'POST'])
def add_car():
    user = users.get(session.get('username'))
    if not isinstance(user, Admin):
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        car_id = len(cars) + 1
        model = request.form['model']
        year = int(request.form['year'])
        color = request.form['color']
        mileage = int(request.form['mileage'])
        accessories = request.form.getlist('accessories')
        image = request.form['image']

        new_car = Car(car_id=car_id, model=model, year=year, image=image, color=color, mileage=mileage, accessories=accessories)
        cars.append(new_car)
        flash(f"Carro {model} adicionado com sucesso!")
        return redirect(url_for('dashboard'))

    return render_template('add_car.html')

@app.route('/admin/remove_car/<int:car_id>')
def remove_car(car_id):
    user = users.get(session.get('username'))
    if not isinstance(user, Admin):
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    car_to_remove = next((c for c in cars if c.car_id == car_id), None)
    if car_to_remove:
        cars.remove(car_to_remove)
        flash("Carro removido com sucesso!")
    else:
        flash("Carro não encontrado.")

    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)