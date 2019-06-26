import os
import time
import zipfile

from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from wtforms import BooleanField, IntegerField, SubmitField, FileField

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.secret_key = 'SYUDxyWO20'


class DownloadForm(FlaskForm):
    split = BooleanField('Split the output file?')
    deduplicate = BooleanField('Remove duplicates from output file?')
    batch = IntegerField("Output file batch size", render_kw={"placeholder": "Output file batch size"})
    submit = SubmitField("Download files as ZIP")


class UploadForm(FlaskForm):
    csv_file = FileField(validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField(u'Upload')


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def chunks(input_list, batch_size):
    for i in range(0, len(input_list), batch_size):
        yield input_list[i:i + batch_size]


@app.route('/downloaded', methods=['GET', 'POST'])
def downloaded():
    request_params = request.args
    print(request_params)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], request_params['filename'])
    batch_size = int(request_params['batch_size'])
    deduplicate = True if request_params['deduplicate'] == 'True' else False
    split = True if request_params['split'] == 'True' else False
    ts = int(round(time.time() * 1000))
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], str(ts))
    os.mkdir(output_dir)
    with open(filepath, 'r') as input_file:
        all_lines = input_file.readlines()
        unique_lines = list(set(all_lines))
        output_list = unique_lines if deduplicate else all_lines
        if split:
            split_list = chunks(output_list, batch_size)
            for idx, s in enumerate(split_list):
                with open(f'{output_dir}/{idx}.csv', 'w') as out_f:
                    out_f.writelines(s)
        else:
            with open(f'{output_dir}/out.csv', 'w') as out_file:
                out_file.writelines(output_list)
    zip_file_name = f'output/{ts}.zip'
    zipper = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(output_dir, zipper)
    zipper.close()
    return send_file(zip_file_name, as_attachment=True)


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    form = DownloadForm()
    if request.method == 'GET':
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as f:
            file_lines = f.readlines()
            all_lines = len(file_lines)
            unique_lines = len(set(file_lines))
        return render_template('download_form.html', form=form, filename=filename, total=all_lines, unique=unique_lines)
    if request.method == 'POST':
        return redirect(url_for('downloaded', filename=filename, batch_size=form.batch.data, split=form.split.data,
                                deduplicate=form.deduplicate.data))


@app.route('/', methods=['GET', 'POST'])
def upload():
    form = UploadForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        f = form.csv_file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('download', filename=filename))
    return render_template('upload_form.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
