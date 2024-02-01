import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField


basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

app = Flask(__name__)

app.config["SECRET_KEY"] = "dfgsfdgsdfgsdfgsdf"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "vaikaitevai.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tevas(db.Model):
    __tablename__ = "tevas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String)
    pavarde = db.Column("Pavardė", db.String)
    vaikas_id = db.Column(db.Integer, db.ForeignKey("vaikas.id"))
    vaikas = db.relationship("Vaikas", cascade="all, delete", passive_deletes=True)


class Vaikas(db.Model):
    __tablename__ = "vaikas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String)
    pavarde = db.Column("Pavardė", db.String)
    tevai = db.relationship("Tevas")


def vaikas_query():
    return Vaikas.query


class TevasForm(FlaskForm):
    vardas = StringField("Vardas", [DataRequired()])
    pavarde = StringField("Pavardė", [DataRequired()])
    vaikas = QuerySelectField(
        query_factory=vaikas_query,
        allow_blank=True,
        get_label="vardas",
        get_pk=lambda obj: str(obj),
    )
    submit = SubmitField("Įvesti")


class VaikasForm(FlaskForm):
    vardas = StringField("Numeris", [DataRequired()])
    pavarde = StringField("Pavardė", [DataRequired()])
    submit = SubmitField("Įvesti")


# @app._got_first_request
# def create_database():
#     with app.app_context():
#         db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tevai")
def parents():
    try:
        visi_tevai = Tevas.query.all()
    except:
        visi_tevai = []
    return render_template("tevai.html", visi_tevai=visi_tevai)


@app.route("/vaikai")
def children():
    try:
        visi_vaikai = Vaikas.query.all()
    except:
        visi_vaikai = []
    return render_template("vaikai.html", visi_vaikai=visi_vaikai)


@app.route("/naujas_tevas", methods=["GET", "POST"])
def new_parent():
    db.create_all()
    forma = TevasForm()
    if forma.validate_on_submit():
        naujas_tevas = Tevas(
            vardas=forma.vardas.data,
            pavarde=forma.pavarde.data,
            vaikas_id=forma.vaikas.data.id,
        )
        db.session.add(naujas_tevas)
        db.session.commit()
        return redirect(url_for("parents"))
    return render_template("prideti_teva.html", form=forma)


@app.route("/delete/<int:id>")
def delete(id):
    uzklausa = Tevas.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for("parents"))


@app.route("/vaikas_delete/<int:id>")
def delete_vaikas(id):
    uzklausa = Vaikas.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for("children"))


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = TevasForm()
    tevas = Tevas.query.get(id)
    if form.validate_on_submit():
        tevas.vardas = form.vardas.data
        tevas.pavarde = form.pavarde.data
        tevas.vaikas_id = form.vaikas.data.id
        db.session.commit()
        return redirect(url_for("parents"))
    return render_template("update.html", form=form, tevas=tevas)


@app.route("/naujas_vaikas", methods=["GET", "POST"])
def new_child():
    db.create_all()
    forma = VaikasForm()
    if forma.validate_on_submit():
        naujas_vaikas = Vaikas(vardas=forma.vardas.data, pavarde=forma.pavarde.data)
        db.session.add(naujas_vaikas)
        db.session.commit()
        return redirect(url_for("children"))
    return render_template("prideti_vaika.html", form=forma)


@app.route("/vaikas_delete/<int:id>")
def vaikas_delete(id):
    uzklausa = Vaikas.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for("children"))


@app.route("/vaikas_update/<int:id>", methods=["GET", "POST"])
def vaikas_update(id):
    form = VaikasForm()
    vaikas = Vaikas.query.get(id)
    if form.validate_on_submit():
        vaikas.vardas = form.vardas.data
        vaikas.pavarde = form.pavarde.data
        db.session.commit()
        return redirect(url_for("children"))
    return render_template("update_vaikas.html", form=form, vaikas=vaikas)


@app.route("/geo")
def location():
    return render_template("geo.html")


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8000, debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
