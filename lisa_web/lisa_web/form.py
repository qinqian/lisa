from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import TextAreaField, BooleanField, SubmitField, SelectMultipleField, SelectField, StringField
from wtforms.validators import DataRequired, Required, length, optional

class LISAForm(FlaskForm):
    genes = TextAreaField('Genes', validators=[Required()])
    name = StringField('Job Name', validators=[Required()])
    method = SelectField("Methods",
                         choices=[
                                  ('knockout', 'In Silico Knockout'),
                                  ('beta', 'BETA'),
                                  ('all', 'All')],
                         default='knockout')
    mark = SelectField("Epigenome Mark",
                       choices=[('H3K27ac', 'H3K27ac'),
                                ('DNase', 'DNase-seq'),
                                ('H3K4me3', 'H3K4me3'),
                                ('H3K27me3', 'H3K27me3'),
                                ('H3K4me1', 'H3K4me1'),
                                ('ATAC-seq', 'ATAC-seq'),
                               ], validators=[Required()], default='H3K27ac')

    species = SelectField("Species", choices=[('hg38', 'human'), ('mm10', 'mouse')], default='hg38')
