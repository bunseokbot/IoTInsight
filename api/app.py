"""Flask Application file."""
from flask import Flask, jsonify, request
from tasks import cloud_service, image_file
from configparser import ConfigParser
from flask_cors import CORS

import os

from parsers.log import log
import parsers.onhub.diagnosticreport_pb2 as diagnostic


_logger = log()

app = Flask(__name__)
app.debug = True
CORS(app)

app.logger.addHandler(_logger._file_handler)

conf = ConfigParser()
conf.read('config.ini')

PACKET_EXTENSIONS = ['.pcap', '.pcapng', '.tcpdump']


def detect_filetype(path):
    """Detect filetype by load file or extensions."""
    filename = os.path.basename(path)

    # detect pcap file by extension name
    for extension in PACKET_EXTENSIONS:
        if filename.endswith(extension):
            return "packet"

    # detect onhub report by loading file to protobuf
    try:
        dr = diagnostic.DiagnosticReport()
        dr.ParseFromString(open(path, 'rb').read())
        return "onhub"
    except:
        pass

    return "other"


@app.route('/task/request/<datatype>', methods=['POST'])
def request_data(datatype):
    """Request data and put into the celery task."""
    data = request.form
    response = {}
    status = 200

    app.logger.debug('Request datatype: {}'.format(datatype))

    if datatype == 'image':
        filetype = data['filetype']
        filepath = data['filepath']

        response['task_id'] = image_file.delay(
            filetype, filepath).task_id

        app.logger.info("Celery Task ID: {} issued".format(response['task_id']))

    elif datatype == 'account':
        service = data['service']

        # check if cloud service access by access_token
        if 'access_token' in data.keys():
            app.logger.debug("Access Token based login cloud service")
            access_token = data['access_token']
            response['task_id'] = cloud_service.delay(service,
                                                      access_token=access_token).task_id
        elif 'username' in data.keys():
            app.logger.debug("Username/Password based login cloud service")
            username = data['username']
            password = data['password']
            response['task_id'] = cloud_service.delay(
                service, username=username, password=password).task_id
        else:
            app.logger.debug("User input based login cloud service")
            response['task_id'] = cloud_service.delay(
                service).task_id

        app.logger.info("Celery Task ID: {} issued".format(response['task_id']))

    else:
        response['message'] = 'Invalid request data type.'
        status = 400

        app.logger.error("Invalid analysis request error: {}".format(datatype))

    return jsonify(response), status


@app.route('/task/status/<id>')
def get_task_id(id):
    """Get task id from celery."""
    app.logger.debug("Request task id {} status check".format(id))
    return jsonify({
        'status': cloud_service.AsyncResult(id).state.lower()
    }), 200


@app.route("/task/bulk", methods=["POST"])
def set_bulk_task():
    """Scan directory and automatic bulk upload."""
    result = {}
    target = request.form['filepath']

    for dirpath, dirnames, filenames in os.walk(target):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            filetype = detect_filetype(filepath)

            result[filepath] = {
                'filetype': filetype,
                'task_id': image_file.delay(filetype, filepath).task_id
            }

    return jsonify(result), 200


if __name__ == '__main__':
    app.logger.info("Starting api server...")
    app.run(
        host='127.0.0.1',
        port=31337,
        threaded=bool(conf['web']['threaded'])
    )
