from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import TextAreaField, BooleanField, SubmitField, SelectMultipleField, SelectField, StringField
from wtforms.validators import DataRequired, Required, length, optional, Email
from wtforms.fields.html5 import EmailField

class LISAForm(FlaskForm):
    genes = TextAreaField('Genes', validators=[Required()])
    labels = StringField('labels', validators=[optional()])

    genes2 = TextAreaField('Genes2', validators=[optional()])
    labels2 = StringField('labels 2', validators=[optional()])

    background = TextAreaField('Background', validators=[optional()])

    name = StringField('Job Name', validators=[optional()]) ## change to optional and give out a warning information
    mail = EmailField('Optional email', validators=[optional(), Email()])
    method = SelectField("Methods",
                         choices=[('knockout', 'ISD-RP for both motif and ChIP-seq'),
                                  ('beta', 'TF ChIP-seq Peak-RP'),
                                  ('all', 'All')],
                         default='all')
    mark = SelectField("Chromatin profile",
                       choices=[('H3K27ac', 'H3K27ac'),
                                ('DNase', 'DNase-seq'),
                                ('All', 'All'),
                                #('H3K4me3', 'H3K4me3'),
                                #('H3K27me3', 'H3K27me3'),
                                #('H3K4me1', 'H3K4me1')
                                #('ATAC-seq', 'ATAC-seq'),
                               ], validators=[Required()], default='All')

    species = SelectField("Species", choices=[('hg38', 'Human'), ('mm10', 'Mouse')], default='hg38')
