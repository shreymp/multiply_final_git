from imports import *

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=20)
    session.modified = True


def generate_problems(num1, num2):
    problems = []
    for n in range(1, num1 + 1):
        for m in range(1, num2 + 1):
            problems.append([n, m])
    random.shuffle(problems)
    return problems


def clear_session():
    for key in list(session.keys()):
        session.pop(key)
    response = redirect('/')
    session.clear()
    return response


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        first_custom_num = request.form['onenum']
        second_custom_num = request.form['twonum']
        if first_custom_num and second_custom_num:
            clear_session()
            session['num1'] = int(first_custom_num)
            session['num2'] = int(second_custom_num)
            return redirect(url_for('multiply', num1=int(first_custom_num), num2=int(second_custom_num)))

    session.pop('problems', None)
    session.pop('completed', None)
    session.clear()
    return render_template('index.html')


@app.route('/multiply/<int:num1>/<int:num2>', methods=['GET', 'POST'])
def multiply(num1, num2):
    if 'problems' not in session:
        session['problems'] = generate_problems(num1, num2)
        session['completed'] = 0

    show_error = False
    total_problems = num1 * num2

    if request.method == 'POST':
        user_answer = int(request.form['ans'])
        correct_answer = session['problems'][0][0] * session['problems'][0][1]

        if user_answer == correct_answer:
            session['problems'].pop(0)
            session['completed'] += 1
        else:
            show_error = True

        if not session['problems']:
            session.pop('problems')
            session.pop('completed')
            clear_session()
            session.clear()
            return redirect(url_for('finished'))

    problem = session['completed'][0]
    return render_template('multiply.html', problem=problem, num1=num1, num2=num2,
                           problems_completed=session['completed'], show_error=show_error, total_problems=total_problems)


@app.route('/finished')
def finished():
    return render_template('finished.html')


if __name__ == '__main__':
    app.run()
