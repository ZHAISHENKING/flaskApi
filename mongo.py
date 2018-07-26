#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import hashlib
import time, datetime
import flask
import pymongo
import bson.binary
import bson.objectid
import bson.errors
from io import BytesIO
from flask import jsonify,json,request,Flask
from flask_cors import CORS
from bson.objectid import ObjectId


app = flask.Flask(__name__)
CORS(app, supports_credentials=True)
app.debug = False
uri = 'localhost:27017'
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
            ("mp4",    "video/mpeg"),
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
    content.seek(0, os.SEEK_END)
    size = content.tell()
    content.seek(0, os.SEEK_SET)
    try:
        # TODO:获取文件类型,文件名 后续可优化
        file = str(f).split(' ')
        filename = file[1].strip("'")
        mime = filename.split('.')[1]
        t = str(time.time())
        str1 = filename + t
        hash1 = hashlib.md5()
        # 编码后存储
        hash1.update(str1.encode('UTF-8'))
        toHash = hash1.hexdigest()
        id = toHash + "." + mime
        if mime not in mimetable.keys():
            raise IOError()
    except IOError:
        flask.abort(400)
    c = dict(
        content=bson.binary.Binary(content.getvalue()),
        mime=mime,
        time=datetime.datetime.utcnow(),
        md5=toHash,
        filename=filename,
        size=size
    )
    try:
        file_set.save(c)
    except pymongo.errors.DuplicateKeyError:
        pass
    return id


def responseto(message=None, error=None, data=None, **kwargs):
    """ 封装 json 响应
    """
    # 如果提供了 data，那么不理任何其他参数，直接响应 data
    if not data:
        data = kwargs
        data['error'] = error
        if message:
            # 除非显示提供 error 的值，否则默认为 True
            # 意思是提供了 message 就代表有 error
            data['message'] = message
            if error is None:
                data['error'] = True
        else:
            # 除非显示提供 error 的值，否则默认为 False
            # 意思是没有提供 message 就代表没有 error
            if error is None:
                data['error'] = False
    if not isinstance(data, dict):
        data = {'error':True, 'message':'data 必须是一个 dict！'}
    resp = jsonify(data)
    # 跨域设置
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers']='*'
    resp.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return resp


@app.route('/docs/f/<id>')
def serve_file(id):
    """
    对文件哈希处理
    """
    md = file_set.find_one({'md5': id.split('.')[0]})
    if md is None:
        raise bson.errors.InvalidId()
    resp = flask.Response(md['content'], mimetype=mimetable[md['mime']])
    resp.headers['Last-Modified'] = md['time'].ctime()
    ctype='*'
    # TODO: 检查原始请求是否指定了Range头部
    if request.headers.get("Range"):
        range_value = request.headers["Range"]
        # print("send_head: range_value=[%s]" % range_value)
        # 直接使用正则表达式匹配: Range: bytes=100-
        HTTP_RANGE_HEADER = re.compile(r'bytes=([0-9]+)\-(([0-9]+)?)')
        m = re.match(HTTP_RANGE_HEADER, range_value)
        if m:
            start_str = m.group(1)
            start = int(start_str)
            end_str = m.group(2)
            end = -1
            if len(end_str) > 0:
                end = int(end_str)
            # 现在可以写Range响应头部了：
            resp.status_code = 206
            resp.headers["Content-Type"] = ctype
            if end == -1:
                resp.headers["Content-Length"] = str(md['size'] - start)
            else:
                resp.headers["Content-Length"] = str(end - start + 1)
            resp.headers["Accept-Ranges"]="bytes"
            if end < 0:
                content_range_header_value = "bytes %d-%d/%d" % (start, md['size'] - 1, md['size'])
            else:
                content_range_header_value = "bytes %d-%d/%d" % (start, end, md['size'])
            resp.headers["Content-Range"] = content_range_header_value
            # print("send_head: ok, serve 206 for Range request %s-%s，Content-Range=%s" % (
            #     start_str, end_str, content_range_header_value))
            resp.headers["Connection"] = "close"
    return resp


@app.route('/docs/upload/', methods=['POST'])
def upload():
  data = request.values
  image = request.files['imgfile']
  video = request.files['videofile']
  imageurl = save_file(image)
  videourl = save_file(video)
  student10 = {"name": data['name'],
               "homeWork": data['homeWork'],
               "comments": data['comments'],
               "videofile": '/f/'+str(videourl),
               "imgfile": '/f/'+str(imageurl),
               "kadaUrl": data['kadaUrl'],
               "title": data['title'],
               "text": data['text'],
               }

  student_id = upload_set.insert_one(student10).inserted_id
  student_ids = str(ObjectId(student_id))
  data = {
      "code": 200,
      "msg": "文件上传成功",
      "data": student_ids
  }
  return responseto(data=data)


@app.route('/docs/student_all/<id>/', methods=['GET'])
def student(id):
    obj = upload_set.find_one({"_id":ObjectId(id)})
    data =  {
        "code": 200,
        "msg": "请求成功",
        "data":{
            'name': obj["name"],
            "homeWork": obj["homeWork"],
            "comments": obj["comments"],
            "videofile": obj["videofile"],
            "imgfile": obj["imgfile"],
            "title": obj["title"],
            "text": obj["text"],
            "kadaUrl": obj["kadaUrl"]
        }
    }
    return responseto(data=data)


@app.route('/docs/')
def index():
  return '''
  <!doctype html>
  <html>
  <body>
  <form action='/docs/upload/' method='post' enctype='multipart/form-data'>
     <input type="text" name="name">
     <input type="text" name="homeWork">
     <input type="textarea" name="comments">
     <input type="text" name="title">
     <input type="text" name="text">
     <input type='file' name='imgfile'>
     <input type='file' name='videofile'>
     <input type='text' name='kadaUrl'>
     <input type='submit' value='Upload'>
  </form>
  '''


if __name__ == '__main__':

  app.run(host='0.0.0.0', port=5000)

