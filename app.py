from flask import Flask, render_template, request, redirect, url_for, session
from tinydb import TinyDB, Query
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
db = TinyDB('checklist_db.json')
sections_table = db.table('sections')
tasks_table = db.table('tasks')
settings_table = db.table('settings')
User = Query()

# Retrieve settings on app start
countdown_settings = settings_table.get(doc_id=1)
if not countdown_settings:
    countdown_settings = {
        'countdown_time': None,
        'countdown_enabled': False
    }
    settings_table.insert(countdown_settings)

@app.route('/')
def index():
    sections = sections_table.all()
    tasks = tasks_table.all()
    countdown_time = countdown_settings.get('countdown_time')
    countdown_enabled = countdown_settings.get('countdown_enabled')
    return render_template('index.html', sections=sections, tasks=tasks, countdown_time=countdown_time, countdown_enabled=countdown_enabled)

@app.route('/admin')
def admin():
    sections = sections_table.all()
    tasks = tasks_table.all()
    countdown_time = countdown_settings.get('countdown_time')
    countdown_enabled = countdown_settings.get('countdown_enabled')
    return render_template('admin.html', sections=sections, tasks=tasks, countdown_time=countdown_time, countdown_enabled=countdown_enabled)

@app.route('/reset_task/<int:task_id>', methods=['POST'])
def reset_task(task_id):
    tasks_table.update({'done_by': None}, doc_ids=[task_id])
    return redirect(url_for('admin'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    tasks_table.remove(doc_ids=[task_id])
    return redirect(url_for('admin'))

@app.route('/reset_all_tasks', methods=['POST'])
def reset_all_tasks():
    tasks_table.update({'done_by': None})
    return redirect(url_for('admin'))

@app.route('/update_countdown', methods=['POST'])
def update_countdown():
    countdown_time = request.form['countdown_time']
    countdown_enabled = 'countdown_enabled' in request.form  # Checkbox presence indicates it's checked
    countdown_settings['countdown_time'] = countdown_time
    countdown_settings['countdown_enabled'] = countdown_enabled
    settings_table.update(countdown_settings, doc_ids=[1])  # Update the settings record
    return redirect(url_for('admin'))

# Route for adding a new section
@app.route('/admin/add_section', methods=['POST'])
def add_section():
    if session.get('username') != 'admin':
        return redirect(url_for('index'))
    section_name = request.form['section_name']
    sections_table.insert({'name': section_name})
    return redirect(url_for('admin'))

# Route for deleting a section
@app.route('/admin/delete_section/<int:section_id>')
def delete_section(section_id):
    if session.get('username') != 'admin':
        return redirect(url_for('index'))
    sections_table.remove(doc_ids=[section_id])
    tasks_table.remove(Query().section_id == section_id)  # Remove tasks related to the section
    return redirect(url_for('admin'))

# Route for adding a new task
@app.route('/admin/add_task', methods=['POST'])
def add_task():
    if session.get('username') != 'admin':
        return redirect(url_for('index'))
    dept = request.form['dept']
    person = request.form['person']
    task_desc = request.form['task']
    try:
        section_id = int(request.form['section_id'])
    except ValueError:
        return redirect(url_for('admin', error="Invalid section ID"))

    tasks_table.insert({
        'dept': dept,
        'person': person,
        'task': task_desc,
        'section_id': section_id,
        'done_by': None  # Initially set to None when not done
    })
    return redirect(url_for('admin'))

# Route for marking a task as done
@app.route('/mark_done/<int:task_id>', methods=["POST"])
def mark_done(task_id):
    if 'username' in session:
        tasks_table.update({'done_by': session['username']}, doc_ids=[task_id])
    return redirect(url_for('index'))

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        if username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('index'))
    return render_template('login.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
