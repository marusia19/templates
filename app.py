from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import datetime

import login_system

import news_sorter

from flask_login import login_required, login_user, logout_user, current_user

import recommender


DATABASE_NAME = 'summertime_webness'

app = Flask(__name__)
 
@app.route("/")
def index():
    filter_options = {}
    tag = request.args.get('tag')
    if tag:
        filter_options['tags'] = {'$in': tag.split(',')}
    news = app.db['news'].find(filter_options).sort([('time', DESCENDING)])

    #sort news
    news = news_sorter.sort_news(news)

    return render_template("index.html", news=news)




@app.route("/news", methods=['POST', 'GET'])
@login_required
def news_handler():
    if request.method == "GET":
        # Get news'

        news = list(app.db['news'].find({}))
        recommended_news = recommender.recommend(current_user.data['name'], news)
        return render_template("news.html", news=recommended_news)
    else:
        title = request.form.get('title', '')
        text = request.form.get('text', '')
        tags = request.form.get('tags', '')
        tags = tags.split(',')
        tags = [tag.strip().lower() for tag in tags]
        # filter empty tags
        # tags = [tag for tag in tags if tag]
        new_tags= []
        for tag in tags:
            if tag:
                new_tags.append(tag)
        tags = new_tags
        tags = list(set(tags))

        new_post = {
            'title': title,
            'text': text,
            'tags': tags,
            'author': current_user.data['name'],
            'time': datetime.datetime.utcnow(),
            'likes': [],
            'dislikes': []
        }
        app.db['news'].insert(new_post)
        return redirect('/')


@app.route('/news/<post_id>', methods=['GET','POST'])
@login_required
def news_post(post_id):
    if request.method == 'GET':
        return redirect('/')
    else:
        action = request.form.get('action')
        post = app.db['news'].find_one(ObjectId(post_id))
        if action == 'like':
            likes = post['likes']\
            #
            likes.append(current_user.data['name'])
            likes = list(set(likes))
            #

            post['likes'] = likes

        app.db['news'].save(post)
        return redirect('/')

@app.route("/users/<user_name>", methods=['GET','POST'])
def profile(user_name):
    if request.method == "GET":
        #user = app.db['users'][user_name]
        user = app.db['users'].find({'name': user_name}).limit(1)[0]
        return render_template("user.html", user=user)
    else:
        full_name = request.form.get('full_name', '')
        skills = request.form.get('skills', '')
        position = request.form.get('position', '')
        photo = request.form.get('photo', '')
        password = request.form.get('password', '')
        # get user object
        #user = app.db['users'][user_name]
        user = app.db['users'].find({'name': user_name}).limit(1)[0]
        user['full_name'] = full_name
        user['position'] = position
        user['photo'] = photo
        user['skills'] = skills
        user['password'] = password
        app.db['users'].save(user)
        return redirect("/users/%s" % user_name)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        next_page = request.args.get('next', '/')
        return render_template("login.html", next_page=next_page)
    else:
        user_name = request.form.get('name' ,'')
        password = request.form.get('password', '')
        next_page = request.form.get('next_page', '/')
        # get user from DB
        users = app.db['users'].find({'name': user_name}).limit(1)
        # Did we find anyone in DB?
        if not users:
            return render_template("login.html", error=True)
        # Lets take the first one
        user = users[0]
        # check password
        if user and password == user['password']:
            # if password is correct, login user
            login_user(login_system.load_user(user_name))
            return redirect(next_page)
        else:
            # if password is not correct, return error page
            return render_template("login.html", error=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route("/users/add")
@login_required
def add_user_page():
    return render_template("add_user.html")

@app.route("/users/<user_name>/edit")
def edit_user(user_name):
    user = app.db['users'].find({'name': user_name}).limit(1)[0]
    return render_template("edit_user.html", user=user)

@app.route("/users", methods=['GET', 'POST'])
def users_handler():
    if request.method == 'GET':
        users = app.db['users'].find()
        return render_template("users.html", users=users)
    elif request.method == 'POST':
        name = request.form.get('name', '')
        full_name = request.form.get('full_name', '')
        skills = request.form.get('skills', '')
        position = request.form.get('position', '')
        photo = request.form.get('photo', '')
        password = request.form.get('password', '')
        new_user = {
            'name': name,
            'full_name': full_name,
            "skills": skills,
            "position": position,
            "photo": photo,
            "password": password,

        }
        #app.db['users'][name] = new_user
        app.db['users'].insert(new_user)
        return redirect("/users/%s" % name)
    else:
        raise RuntimeError("Only POST and GET methods are supported")
 
 
if __name__ == "__main__":

    app.db = MongoClient('wardoctor.nosoc.io', port=443)[DATABASE_NAME]
    login_system.init_login_system(app)
    app.run(debug=True)

    # style="background-image:url(https://pp.vk.me/c618426/v618426104/12476/CtRpXTwpsKk.jpg)"
