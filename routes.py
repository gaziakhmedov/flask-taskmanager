from flask import *
from functools import wraps
import sqlite3

DATABASE = 'flasktask.db'

app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = 'secret'

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('Для начала Вам нужно залогиниться.')
            return redirect(url_for('log'))
    return wrap

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Вы вышли из системы')
    return redirect (url_for('log'))

@app.route('/tasks')
@login_required
def tasks():
    g.db  = connect_db()
    cur = g.db.execute('select name, due_date, priority, task_id from ftasks where status=1')
    open_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cur.fetchall()]
    cur = g.db.execute('select name, due_date, priority, task_id from ftasks where status=0')
    closed_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cur.fetchall()]
    g.db.close()
    return render_template('tasks.html', open_tasks=open_tasks, closed_tasks=closed_tasks)

@app.route('/add', methods=['POST'])
@login_required
def new_task():
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']
    if not name and not date and not priority:
        flash("Вы неправильно ввели Название задачи, дату и приоритет. Попробуйте ещё раз.")
        return redirect(url_for('tasks'))
    elif not name and not date:
        flash("Вы неправильно ввели Название задачи и Дату. Попробуйте ещё раз.")
        return redirect(url_for('tasks'))
    elif not date and not priority:
        flash("Вы неправильно ввели Название задачи и Дату. Попробуйте ещё раз.")
        return redirect(url_for('tasks'))
    elif not name and not priority:
        flash("Вы неправильно ввели Название задачи и Приоритет! Попробуйте ещё раз.")
        return redirect(url_for('tasks'))   
    elif not name:
        flash("Вы неправильно ввели Название задачи! Попробуйте ещё раз.")
        return redirect(url_for('tasks'))
    elif not date:
        flash("Вы неправильно ввели Дату задачи! Попробуйте ещё раз.")
        return redirect(url_for('tasks'))
    elif not priority:
        flash("Вы неправильно ввели Приоритет Задачи! Try again.")
        return redirect(url_for('tasks'))    
    else:
        g.db.execute('insert into ftasks (name, due_date, priority, status) values (?, ?, ?, 1)',
             [request.form['name'], request.form['due_date'], request.form['priority']])                 
        g.db.commit()
        flash('Новая задача была опубликована.')
        return redirect(url_for('tasks'))

@app.route('/delete/<int:task_id>',)
@login_required
def delete_entry(task_id):
    g.db  = connect_db()
    cur = g.db.execute('delete from ftasks where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('Задача была удалена.')
    return redirect(url_for('tasks'))

@app.route('/complete/<int:task_id>',)
@login_required
def complete(task_id):
    g.db  = connect_db()
    cur = g.db.execute('update ftasks set status = 0 where task_id='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('Задача была выполнена.')
    return redirect(url_for('tasks'))




@app.route('/', methods=['GET', 'POST'])
def log():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Вы ввели неправильный логин/пароль. Попробуйте ещё раз.'
        else:
            session['logged_in'] = True
        return redirect(url_for('tasks'))
    return render_template('log.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
