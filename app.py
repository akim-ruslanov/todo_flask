from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime)
    tag = db.Column(db.Text)  # might create enumeration???
    done = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    def __init__(self, title, due_date, tag, project_id):
        self.title = title
        self.due_date = due_date
        # self.date_created = datetime.utcnow
        self.tag = tag  # check what happens when tag is empty 
        self.done = False
        self.project_id = project_id

    def __repr__(self):
        return '<Task Title %s>' % self.title


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True, default="")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='project', lazy=True)

    def __init__(self, title, description):
        self.title = title
        self.description = description

    def __repr__(self):
        return '<Project Title %s>' % self.title


db.create_all()


@app.route('/')
def tasks_list():
    projects = Project.query.all()
    if (len(projects) != 0):
        project_active = projects[0]
    else:
        project_active = -1
    return render_template('index.html', projects=projects, project_active=project_active)


@app.route('/project_page')
def add_project_page():
    projects = Project.query.all()
    return render_template('add_project.html', projects=projects)

@app.route('/about')
def about():
    projects = Project.query.all()
    return render_template('about.html', projects=projects)

@app.route('/<int:project_id>')
def project_tasks(project_id):
    projects = Project.query.all()
    if (len(projects) == 0):
        return render_template('index.html', projects=projects, project_active=-1)
    project_active = Project.query.get(project_id)
    return render_template('index.html', projects=projects, project_active=project_active)


@app.route('/project', methods=['POST'])
def add_project():
    title = request.form['title']
    desc = request.form['desc']
    if not title:
        return redirect('/')  # stub
    project = Project(title, desc)
    db.session.add(project)
    db.session.commit()
    return redirect('/')


@app.route('/task/<int:project_id>', methods=['POST'])
def add_task(project_id):
    title = request.form['title']
    due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')  
    # project_id = int(request.form['project_id'])
    project_id = project_id
    print(request.form)
    if not title:
        # alert user
        return redirect('/')
    task = Task(title, due_date, '', project_id)
    db.session.add(task)
    db.session.commit()
    return redirect('/')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect('/')
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    project = Project.query.get(project_id)
    projects = Project.query.all()
    if not Project:
        return redirect('/'+project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect('/'+str(project_id))



@app.route('/done/<int:task_id>')
def resolve_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect('/')
    if task.done:
        task.done = False
    else:
        task.done = True
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
