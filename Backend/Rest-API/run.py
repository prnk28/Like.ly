## Run.py
## Pradyumn Nukala
## June 23, 2017
## Description: Main runner class to initialize eve instance onto server.
##              This file is a copy of the file that exists on our linux vm.

from eve import Eve
from eve.auth import BasicAuth

class BasicAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource,
                   method):
        return username == 'admin' and password == 'braxday123'

app = Eve(auth=BasicAuth)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
