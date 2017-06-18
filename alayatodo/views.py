from alayatodo import app, db
from functools import wraps
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify,
    abort
    )
from models import (User, Todo)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function    


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username, password=password).first_or_404()
    if user:
        session['user_id'] = user.id
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user.id != g.user.id:
        abort(401)
    return render_template('todo.html', todo=todo)

@app.route('/todo/<id>', methods=['POST', 'PUT'])
def todo_update(id):
    todo = Todo.query.get_or_404(id)
    if todo.user.id != g.user.id:
        abort(401)
    todo.completed = request.form.get('completed', '0') == '1'
    db.session.commit()
    return redirect(request.referrer or url_for('todo', id=id))

@app.route('/todo/<id>', methods=['DELETE'])
def todo_delete(id):
    todo = Todo.query.get_or_404(id)
    if todo.user.id != g.user.id:
        abort(401)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted, congrats!', 'success')
    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    todo = Todo.query.get_or_404(id)
    if todo.user.id != g.user.id:
        abort(401)
    return jsonify(todo.as_dict())


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 2))
    return render_template('todos.html', todos=g.user.todos.paginate(page, per_page))


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    try:
        todo = Todo(user=g.user, description=request.form.get('description', ''))
        db.session.add(todo)
        db.session.commit()
    except ValueError as e:
        flash('Cannot add the todo: %s' % (e,), 'danger')
        return render_template('todos.html', todos=g.user.todos)
    flash('Todo added, now work hard to complete it!', 'success')
    return redirect(request.referrer or url_for('todos'))