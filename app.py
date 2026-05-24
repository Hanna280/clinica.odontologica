from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
from models import db, Usuario, Paciente, Consulta

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(
            email=email,
            senha=senha
        ).first()

        if usuario:
            login_user(usuario)
            return redirect('/dashboard')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():

    total_pacientes = Paciente.query.count()
    total_consultas = Consulta.query.count()

    return render_template(
        'dashboard.html',
        pacientes=total_pacientes,
        consultas=total_consultas
    )

@app.route('/pacientes')
@login_required
def pacientes():

    lista_pacientes = Paciente.query.all()

    return render_template(
        'pacientes.html',
        pacientes=lista_pacientes
    )
    
@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):

    paciente = Paciente.query.get(id)

    if request.method == 'POST':

        paciente.nome = request.form['nome']
        paciente.telefone = request.form['telefone']

        db.session.commit()

        return redirect('/pacientes')

    return render_template(
        'editar_paciente.html',
        paciente=paciente
    )


@app.route('/excluir_paciente/<int:id>')
@login_required
def excluir_paciente(id):

    paciente = Paciente.query.get(id)

    db.session.delete(paciente)
    db.session.commit()

    return redirect('/pacientes')

@app.route('/consultas', methods=['GET', 'POST'])
@login_required
def consultas():

    if request.method == 'POST':

        nova = Consulta(
            paciente=request.form['paciente'],
            data=request.form['data'],
            horario=request.form['horario']
        )

        db.session.add(nova)
        db.session.commit()

    lista_consultas = Consulta.query.all()

    return render_template(
        'consultas.html',
        consultas=lista_consultas
    )

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

        if not Usuario.query.filter_by(email='admin@admin.com').first():

            admin = Usuario(
                nome='Administrador',
                email='admin@admin.com',
                senha='123'
            )

            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)