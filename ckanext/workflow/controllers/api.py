# encoding: utf-8
from ckan.common import request, response
import json
import re
import zipfile
import StringIO


CONTENT_TYPES = {
    'text': 'text/plain;charset=utf-8',
    'html': 'text/html;charset=utf-8',
    'json': 'application/json;charset=utf-8',
    'octet-stream': 'application/octet-stream;charset=utf-8',
}

def download_multiple(fn):
    def decorate_finish_ok(self, response_data=None,
                   content_type='json',
                   resource_location=None):
        '''This function is based on the core function plus extras.
           It checks param ids to get the ids of packages and param
           download. If true, it will change the header for download
           type.
        @param resource_location - specify this if a new
           resource has just been created.
        @return response message - return this value from the controller
                                   method
                                   e.g. return self._finish_ok(pkg_dict)
        '''
        flag = False
        if request.params.get('download'):
            content_type='octet-stream'
            if request.params.get('ids'):
                response.headers['Content-Disposition'] = "attachment; filename=batch.zip"
                flag = True
            elif not response.headers.has_key('Content-Disposition'):
                response.headers['Content-Disposition'] = "attachment; filename=none.txt"

            if flag:
                # handle the batch zip file with each dataset txt file
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                os = []
                names = []
                for d in response_data['result']:
                    o = StringIO.StringIO()
                    o.write(json.dumps(d, indent=2))
                    os.append(o)
                    names.append(d['name'])
                oz = StringIO.StringIO()
                with zipfile.ZipFile(oz, 'a') as myzip:
                    for idx, o in enumerate(os):
                      myzip.writestr(names[idx] + ".txt", o.getvalue())
                      o.close()
                response_data = oz.getvalue()
                oz.close()
            elif not flag and isinstance(response_data, dict):
                response_data = json.dumps(response_data, indent=2)

        return fn(self, response_data, content_type, resource_location)

    return decorate_finish_ok