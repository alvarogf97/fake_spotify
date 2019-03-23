ALLOWED_EXTENSIONS = {'mp3', 'wma'}


def crop_withespaces(string: str):
    return "_".join(string.split())


def uncrop_withespaces(string: str):
    return " ".join(string.split('_'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
