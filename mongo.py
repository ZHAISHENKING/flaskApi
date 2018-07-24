import hashlib
import datetime
import flask
import pymongo
import bson.binary
import bson.objectid
import bson.errors
from io import BytesIO
from flask import jsonify,json,request,Flask
from bson.objectid import ObjectId

app = flask.Flask(__name__)
app.debug = False
uri = 'mongodb://jamie:jamie199469@localhost:27676/ultrabear_homework'
client = pymongo.MongoClient(uri)
upload_set = client['ultrabear_homework'].day
file_set = client['ultrabear_homework'].file

mimetable=dict([
            ("3gp",    "video/3gpp"),
            ("apk",    "application/vndandroidpackage-archive"),
            ("asf",    "video/x-ms-asf"),
            ("avi",    "video/x-msvideo"),
            ("bin",    "application/octet-stream"),
            ("bmp",    "image/bmp"),
            ("c",  "text/plain"),
            ("class",  "application/octet-stream"),
            ("conf",   "text/plain"),
            ("cpp",    "text/plain"),
            ("doc",    "application/msword"),
            ("docx",   "application/vndopenxmlformats-officedocumentwordprocessingmldocument"),
            ("xls",    "application/vndms-excel"),
            ("xlsx",   "application/vndopenxmlformats-officedocumentspreadsheetmlsheet"),
            ("exe",    "application/octet-stream"),
            ("gif",    "image/gif"),
            ("gtar",   "application/x-gtar"),
            ("gz", "application/x-gzip"),
            ("h",  "text/plain"),
            ("htm",    "text/html"),
            ("html",   "text/html"),
            ("jar",    "application/java-archive"),
            ("java",   "text/plain"),
            ("jpeg",   "image/jpeg"),
            ("jpg",    "image/jpeg"),
            ("js", "application/x-javascript"),
            ("log",    "text/plain"),
            ("m3u",    "audio/x-mpegurl"),
            ("m4a",    "audio/mp4a-latm"),
            ("m4b",    "audio/mp4a-latm"),
            ("m4p",    "audio/mp4a-latm"),
            ("m4u",    "video/vndmpegurl"),
            ("m4v",    "video/x-m4v"),
            ("mov",    "video/quicktime"),
            ("mp2",    "audio/x-mpeg"),
            ("mp3",    "audio/x-mpeg"),
            ("mp4",    "video/mp4"),
            ("mpc",    "application/vndmpohuncertificate"),
            ("mpe",    "video/mpeg"),
            ("mpeg",   "video/mpeg"),
            ("mpg",    "video/mpeg"),
            ("mpg4",   "video/mp4"),
            ("mpga",   "audio/mpeg"),
            ("msg",    "application/vndms-outlook"),
            ("ogg",    "audio/ogg"),
            ("pdf",    "application/pdf"),
            ("png",    "image/png"),
            ("pps",    "application/vndms-powerpoint"),
            ("ppt",    "application/vndms-powerpoint"),
            ("pptx",   "application/vndopenxmlformats-officedocumentpresentationmlpresentation"),
            ("prop",   "text/plain"),
            ("rc", "text/plain"),
            ("rmvb",   "audio/x-pn-realaudio"),
            ("rtf",    "application/rtf"),
            ("sh", "text/plain"),
            ("tar",    "application/x-tar"),
            ("tgz",    "application/x-compressed"),
            ("txt",    "text/plain"),
            ("wav",    "audio/x-wav"),
            ("wma",    "audio/x-ms-wma"),
            ("wmv",    "audio/x-ms-wmv"),
            ("wps",    "application/vndms-works"),
            ("xml",    "text/plain"),
            ("z",  "application/x-compress"),
            ("zip",    "application/x-zip-compressed"),
        ])


def save_file(f):
  content = BytesIO(f.read())
  try:
    # mime = Image.open(content).format.lower()
    # TODO:获取文件类型,文件名 后续可优化
    file = str(f).split(' ')
    filename = file[1].strip("'")
    mime = filename.split('.')[1]
    if mime not in mimetable.keys():
      raise IOError()
  except IOError:
    flask.abort(400)
  sha1 = hashlib.sha1(content.getvalue()).hexdigest()
  c = dict(
    content=bson.binary.Binary(content.getvalue()),
    mime=mime,
    time=datetime.datetime.utcnow(),
    sha1=sha1,
    filename=filename,
  )
  try:
    file_set.save(c)
  except pymongo.errors.DuplicateKeyError:
    pass
  return sha1


@app.route('/test1')
def hello():
    return 'hello world'


@app.route('/f/<sha1>')
def serve_file(sha1):
  """
  对文件哈希处理
  """

  try:
    f = file_set.find_one({'sha1': sha1})
    if f is None:
      raise bson.errors.InvalidId()
    if request.headers.get('If-Modified-Since') == f['time'].ctime():
      return flask.Response(status=304)
    resp = flask.Response(f['content'], mimetype=mimetable[f['mime']])
    resp.headers['Last-Modified'] = f['time'].ctime()
    return resp
  except bson.errors.InvalidId:
    flask.abort(404)


@app.route('/upload', methods=['POST'])
def upload():
  data = request.values
  image = request.files['imgurl']
  video = request.files['videoUrl']
  imageurl = save_file(image)
  videourl = save_file(video)
  student10 = {"name": data['name'],
               "homeWork": data['homeWork'],
               "comments": data['comments'],
               "videoUrl": '/f/'+str(videourl),
               "imgurl": '/f/'+str(imageurl),
               "kadaUrl": data['kadaUrl'],
               "titel": data['titel'],
               "text": data['text'],
               }

  student_id = upload_set.insert_one(student10).inserted_id
  student_ids = str(ObjectId(student_id))
  return jsonify({
      "code": 200,
      "msg": "文件上传成功",
      "data": student_ids
  })


@app.route('/student_all/<id>', methods=['GET'])
def student(id):
    obj = upload_set.find_one({"_id":ObjectId(id)})
    return jsonify({
        "code": 200,
        "msg": "请求成功",
        "data":{
            'name': obj["name"],
            "homeWork": obj["homeWork"],
            "comments": obj["comments"],
            "videoUrl": obj["videoUrl"],
            "imgurl": obj["imgurl"],
            "titel": obj["titel"],
            "text": obj["text"],
            "kadaUrl": obj["kadaUrl"]
        }
    })


@app.route('/')
def index():
  return '''
  <!doctype html>
  <html>
  <body>
  <form action='/upload' method='post' enctype='multipart/form-data'>
     <input type="text" name="name">
     <input type="text" name="homeWork">
     <input type="textarea" name="comments">
     <input type="text" name="titel">
     <input type="text" name="text">
     <input type='file' name='imgurl'>
     <input type='file' name='videoUrl'>
     <input type='text' name='kadaUrl'>
     <input type='submit' value='Upload'>
  </form>
  '''


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
