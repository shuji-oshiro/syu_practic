from flask import Flask, render_template, redirect
from forms import NameForm
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベース初期化
db.init_app(app)

with app.app_context():
    db.create_all()  # 初回のみテーブル作成

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    users = User.query.all()

    if form.validate_on_submit():
        new_user = User(name=form.name.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')  # リロードで再送信防止

    return render_template('index.html', form=form, users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
