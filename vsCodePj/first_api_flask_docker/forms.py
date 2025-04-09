from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from wtforms.validators import ValidationError


    
class NameForm(FlaskForm):
    def only_kanji(form, field):# 日本語チェックのカスタムバリデータ
        # field.data = field.data.replace(" ", "")  # 空白を削除（必要に応じて）
        if not field.data.isalpha():  # 簡易な例（全て日本語チェックなどに応用可能）
            raise ValidationError("文字のみで入力してください")

    name = StringField('お名前', validators=[
        DataRequired(message="名前は必須"),
        Length(min=2, max=20, message="2〜20文字で入力してください"),
        only_kanji
    ])
    submit = SubmitField('送信')


