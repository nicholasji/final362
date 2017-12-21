#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Book Catalogue

from flask import Flask, render_template, request, redirect, session, g, flash, url_for
import os, requests, sqlite3, validators

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'bookcatalogue.db'),
    SECRET_KEY='password'
    ))


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.route('/')
def init():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select id from users where username=? and password=?', [request.form['username'], request.form['password']])
        validUser = cur.fetchone()
        if validUser:
            session['logged_in'] = True
            session['user_id'] = validUser[0]
            flash('Logged in')
            return redirect(url_for('my_books'))
        else:
            session['logged_in'] = False
            error = 'Invalid Username or Password'
    return render_template('login.html', error=error)


@app.route('/mybooks', methods=['GET'])
def my_books():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    db = get_db()
    cur = db.execute('select user_id, title, author, pgcnt, avgrating, thumbnail from bookcatalogue where user_id=?', [session['user_id']])
    books = cur.fetchall()
    return render_template('mybooks.html', books=books)


@app.route('/searchbooks', methods=['GET', 'POST'])
def search_books():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        
        r = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:' + request.form['isbnnumber'])
        json = r.json()
        searchresults = []
        for item in json['items']:
            result = {}
            result['title'] = item['volumeInfo']['title']
            
            if 'authors' in item['volumeInfo'].keys():
                result['author'] = item['volumeInfo']['authors'][0]
            else:
                result['author'] = 'Author not found'
            
            if 'pageCount' in item['volumeInfo'].keys():
                result['pageCount'] = item['volumeInfo']['pageCount']
            else:
                result['pageCount'] = 'Page count not found'
            
            if 'averageRating' in item['volumeInfo'].keys():
                result['averageRating'] = item['volumeInfo']['averageRating']
            else:
                result['averageRating'] = 'Average rating not found'
            
            if 'imageLinks' in item['volumeInfo'].keys():
                result['thumbnail'] = item['volumeInfo']['imageLinks']['thumbnail']
            else:
                result['thumbnail'] = 'Thumbnail not found'
            searchresults.append(result)
        return render_template('searchbooks.html', searchresults=searchresults)
    return render_template('searchbooks.html')



@app.route('/addbook', methods=['GET'])
def add_book():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    db = get_db()
    cur = db.execute('insert into bookcatalogue (user_id, title, author, pgcnt, avgrating, thumbnail) values (?, ?, ?, ?, ?, ?)', [session['user_id'], request.args['title'], request.args['author'], request.args['pageCount'], request.args['averageRating'], request.args['thumbnail']])
    db.commit()
    return redirect(url_for('my_books'))


@app.route('/deletebook', methods=['GET'])
def delete_book():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    db = get_db()
    cur = db.execute('delete from bookcatalogue where user_id=? and title=? and author=? and pgcnt=? and avgrating=? and thumbnail=?', [session['user_id'], request.args['title'], request.args['author'], request.args['pageCount'], request.args['averageRating'], request.args['thumbnail']])
    db.commit()
    return redirect(url_for('my_books'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out')
    return redirect('/login')




if __name__ == '__main__':
    app.run()
