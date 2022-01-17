import os
from flask import (
    Flask, render_template, redirect,
    request, session, url_for, flash)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/base")
def base():
    return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}!".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists...")
            return redirect(url_for("register"))

        register = {
            "name": request.form.get("name").lower(),
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
        }
        mongo.db.users.insert_one(register)

        session["user"] =request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/post_show", methods=["GET", "POST"])
def post_show():
    if request.method == "POST":
        # Bara för att se vad som skickas till dbn - visas i konsolfönstret. Ej nödvändig.
        req = request.form # Sparar allt från seriestabellen
        print(req) # Printar i konsolen    
        
        selection = {
            "country": request.form.get("country"),
            "director": request.form.get("director"),
            "genre": request.form.get("genre"),
            "parental_guidance": request.form.get("parental_guidance"),
            "picture": request.form.get("picture"),
            "seasons": request.form.get("seasons"),
            "starring": request.form.get("starring"),
            "synopsis": request.form.get("synopsis"),
            "title": request.form.get("title"),
            "year": request.form.get("year"),
            "posted_by": session["user"],
        }
        mongo.db.series.insert_one(selection)       
        flash("Post Successful!")
        return redirect(request.url)
    
    return render_template("post_show.html")


@app.route("/cards")
def cards():
    cards = mongo.db.series.find({})
    return render_template("cards.html", cards=cards)


@app.route("/update_show/<show_id>", methods=["GET", "POST"])
def update_show(show_id):
    show = mongo.db.series.find_one({"_id": ObjectId(show_id)})
    return render_template("update_show.html", show=show)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
# above "/profile/" is the app route "<username>" is an argument, named username as we expect the users username to be passed into the route
    # now the profile function takes the username argument, passed into the profile route function
def profile(username): # <<<< here

    # below is a query to the database to find one user where "username" matches session["user"]
    username = mongo.db.users.find_one(
        {"username": session["user"]})

    # HERE is where the data on the cards objects begins
    # the query is made to the database to find any series objects where "posted_by" matches session["user"]
    cards = mongo.db.series.find(
        {"posted_by": session["user"]})

    if session["user"]:
        # in the render_template() method, we pass data from this function into the template
        # we defined that data
        # username=username takes the data returned on line 133 and defines it as 'username'
        # we can now access 'username' on the template

        # the same for cards=cards, this is defining 'cards' and assigning it the value of whats returned
        # from the database query on line 138
        # on the template, 'cards' will be equal to 'cards' as defined on line 138
        # this is what's called passing the data to the template as context
        return render_template("profile.html", username=username, cards=cards)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/ratings", methods=["GET", "POST"])
def ratings():
    if request.method == "POST":
        # Bara för att se vad som skickas till dbn - visas i konsolfönstret. Ej nödvändig.
        req = request.form # Sparar allt från tabellen
        print(req) # Printar i konsolen    
        
        grades = {
            "rating": request.form.get("rating"),
            "review": request.form.get("review"),
            "created_by": session["user"],
            "show": request.form.get("show"),
        }
        mongo.db.ratings.insert_one(grades)       
        flash("Rating Successful!")
        return redirect(request.url)
    cards = list(mongo.db.series.find({}))
    reviews = list(mongo.db.ratings.find({}))
    return render_template("cards.html", cards=cards, reviews=reviews)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)