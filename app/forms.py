from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length


class BookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=300)])
    gid = StringField("gid", validators=[DataRequired(), Length(max=50)])
    publication_date = DateTimeField("Publication date", format="%Y/%m/%d")
    number_of_pages = IntegerField("Number of pages")
    language = StringField("Language", validators=[DataRequired(), Length(max=10)])
    image_link = StringField("Image link", validators=[Length(max=400)])
    isbn_10 = StringField("ISBN 10", validators=[Length(min=10, max=10)])
    isbn_13 = StringField("ISBN 13", validators=[Length(min=13, max=13)])
    authors = StringField('Authors ( separated by "," )')
    submit = SubmitField("Save")
