from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, render_template, request, make_response, redirect, session, url_for
import jsonrpclib
import psycopg2
from Db import db
from Db.models import users, book
from flask_login import login_user, login_required, current_user, logout_user
main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
@main.route("/main", methods=["GET", "POST"])
def mainpage():
    try:
        username = users.query.filter_by(id=current_user.id).first().username
    except:
        username = "Аноним"
    # Получить название, автора, количество страниц от, количество страниц до и издателя из запроса
    title = request.args.get("title")
    author = request.args.get("author")
    pages_from = request.args.get("pages_from")
    pages_to = request.args.get("pages_to")
    publisher = request.args.get("publisher")

    ##Фильтр
    if title is not None:
        books = book.query.filter(book.title.like(f"%{title}%"))
    if author is not None:
        books = books.filter(book.author.like(f"%{author}%"))
    if pages_from is not None:
        try:
            pages_from = int(pages_from)
            books = books.filter(book.pages >= pages_from)
        except ValueError:
            pass
    if pages_to is not None:
        try:
            pages_to = int(pages_to)
            books = books.filter(book.pages <= pages_to)
        except ValueError:
            pass
    if publisher is not None:
        books = books.filter(book.publisher.like(f"%{publisher}%"))
    else:
        books = book.query.all()

    return render_template('main_page.html', books=books, username=username)

@main.route("/main/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "GET":
        return render_template("register.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")

    existing_user = users.query.filter_by(username=username_form).first()
    if username_form == '':
        errors.append('Имя пользователя не может быть пустым!')
    elif existing_user is not None:
        errors.append('Пользователь с таким именем уже существует!')
    elif len(password_form) < 5:
        errors.append('Пароль должен быть длиннее 5 символов!')
    else:
        user = users.query.filter_by(username=username_form).first()
        if user is not None:
            if user.is_superuser:
                errors.append('Пользователь уже является администратором!')
            else:
                hashed_password = generate_password_hash(password_form, method='pbkdf2')
                new_user = users(username=username_form, password=hashed_password, is_superuser=False)
                db.session.add(new_user)
                db.session.commit()
                return redirect("/main")
        else:
            hashed_password = generate_password_hash(password_form, method='pbkdf2')
            new_user = users(username=username_form, password=hashed_password, is_superuser=False)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/main")

    return render_template("register.html", errors=errors)


@main.route("/main/login", methods=["GET", "POST"])
def login():
    errors = []
    if request.method == "GET":
        return render_template("login.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")

    my_user = users.query.filter_by(username=username_form).first()
    if username_form is None or password_form is None:
        errors.append("Заполните все поля!")
        return render_template("login.html", errors=errors)
    else:
        if my_user is not None:
            if check_password_hash(my_user.password, password_form):
                login_user(my_user)
                return redirect("/main")
            else:
                errors.append("Неверный пароль!")
                return render_template("login.html", errors=errors)
        else:
            errors.append("Пользвателя с таким именем не существует!")
            return render_template("login.html", errors=errors)

        
    
@main.route("/main/logout")
@login_required
def logout():
    logout_user()
    return redirect("/main/login")

@main.route("/add_book", methods=["GET", "POST"])
def add_book():
    is_admin = current_user.is_authenticated and current_user.is_superuser
    if not is_admin:
        return redirect('/main')
    errors = []
    if request.method == "GET":
        return render_template("add_book.html")

    title_form = request.form.get("title")
    author_form = request.form.get("author")
    pages_form = request.form.get("pages")
    publisher_form = request.form.get("publisher")
    cover_url_form = request.form.get("cover_url")

    if title_form == '':
        errors.append('Название книги не может быть пустым!')
    elif author_form == '':
        errors.append('Автор книги не может быть пустым!')
    elif pages_form == '':
        errors.append('Количество страниц книги не может быть пустым!')
    elif not pages_form.isdigit():
        errors.append('Количество страниц книги должно быть целым числом!')
    elif publisher_form == '':
        errors.append('Издательство книги не может быть пустым!')
    else:
        if cover_url_form:
            cover_url = cover_url_form
        else:
            errors.append('Ссылка на картинку отсутствует!')

        if not errors:
            new_book = book(title=title_form, author=author_form, pages=int(pages_form), publisher=publisher_form, cover_url=cover_url)
            db.session.add(new_book)
            db.session.commit()

    return render_template("add_book.html", errors=errors)


@main.route("/edit_book/<int:id>", methods =["GET", "POST"])
def edit_book(id):
    if current_user.is_authenticated or current_user.is_superuser:
        pook = book.query.get(id)

        if request.method == "GET":
            return render_template("editbook.html", book=pook)

        if request.method == "POST":
            book.title = request.form.get("title")
            book.author = request.form.get("author")
            book.pages = request.form.get("pages")
            book.publisher = request.form.get("publisher")

            db.session.commit()

            return redirect('/main')
    else:
        return render_template("main_page.html",
                                username=current_user.username,
                                books=book.query.all())


@main.route("/delete_book/<int:id>", methods=["GET", "POST"])
def delete_book(id):
    if current_user.is_authenticated or current_user.is_superuser:
        pook = book.query.get(id)

        if request.method == "GET":
            return render_template("deletebook.html", book=pook)

        if request.method == "POST":
            db.session.delete(pook)
            db.session.commit()

            return redirect("/main")
    else:
        return render_template("main_page.html", username=current_user.username, books=book.query.all())
