from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route('/')
def home():
    return render_template('index.html', nums={1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'})


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         user = request.form['name']       # uzimamo vrijednost varijable "name" iz login.html-a
#                                           # request.form dolazi u obliku dictionarija, gdje je ključ naziv varijable iz html-a,
#                                           # a value je vrijednost koju submitamo na stranici
#         return redirect(url_for('user', name=user))    # redirectamo na stranicu "user" te kao input uzimamo
#                                                        # vrijednost koju smo submitali i spremili u varijablu "user"
#     else:
#         return render_template('login.html')
#
## dinamično postavljanje adrese - što god upišemo u address bar, biti će prikazano kao adresa stranice
# @app.route('/<name>')
# def user(name):
#     return f'Hello there <h3>{name}</h3> how are you?'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['name']

        if user == "":
            return render_template('login.html', user=user)
        else:
         # session je dictionary, služi za privremeno spremanje login podataka o useru, npr. session = {'user': 'Marko'}
            session['user'] = user

            found_user = Users.query.filter_by(name=user).first()

            if found_user:
                session['email'] = found_user.email
            else:
                usr = Users(user, '')
                db.session.add(usr)
                db.session.commit()

            flash(f'You have logged in successfully, {user}!')
            return redirect(url_for('user'))
    else:
        # ako smo ulogirani i stisnemo na Login, prebacujemo se na ekran za update maila
        if 'user' in session:
            user = session['user']
            found_name = Users.query.filter_by(name=user).first()

            return render_template('update.html', user=found_name)
        return render_template('login.html')


email_addresses = {}


@app.route('/user', methods=['POST', 'GET'])
def user():
    email = None

    # provjeravamo da li ključ "user" postoji. Postojat će samo ako smo se ulogirali (vidi gore login funkciju)
    if 'user' in session:
        user = session['user']

        if request.method == 'POST':
            email = request.form['email']

            if email != '':

                # provjeravamo je li mail adresa u dictionariju, odnosno da li već postoji
                if email in email_addresses.values():
                    flash('This email address has already been submitted, enter another one!')
                else:
                    session['email'] = email

                    found_user = Users.query.filter_by(name=user).first()
                    found_user.email = email
                    db.session.commit()

                    flash(f'You have successfully submitted your email, {user}!')

                # dodajemo email adresu u dictionary ili mijenjamo ključ ako unosimo 2.mail adresu za jednog korisnika
                    email_addresses[session['user']] = email

        else:
            if 'email' in session:
                email = session['email']
        return render_template('logout.html', email=email, user=user)
    else:
        return redirect(url_for('login'))


@app.route('/view')
def view():
    return render_template('view.html', values=Users.query.all())


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    user_for_update = Users.query.get(id)

    if request.method == 'POST':
        email = request.form['update']
        user_for_update.email = email
        email_addresses[session['user']] = email
        db.session.commit()

        return redirect(url_for('view'))

    else:
        return render_template('update.html', user=user_for_update)


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get(id)

    # ako mail adresa korisnika kojeg brišemo postoji onda ju brišemo iz dictionarija
    if user_to_delete.email in email_addresses.values():
        email_addresses.pop(user_to_delete.name)

    # ako smo ulogirani i brišemo podatak o useru s kojim smo ulogirani, onda se automatski logout-amo nakon brisanja
    if 'user' in session:
        if user_to_delete.name == session['user']:
            session.pop('user', None)

    db.session.delete(user_to_delete)
    db.session.commit()

    return redirect(url_for('view'))


@app.route('/logout')
def logout():
    if 'user' in session:
        user = session['user']
        flash(f'You have logged out successfully, {user}!')

    # brišemo podatke o useru koje smo spremili prilikom logiranja
    session.pop('user', None)
    session.pop('email', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

