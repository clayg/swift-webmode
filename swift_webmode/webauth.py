from urlparse import parse_qs

class WebAuthMiddleware(object):

    def __init__(self, app, conf):
        self.app = app
        self.conf = conf

    def handle_login(self, env, start_response):
        if env['REQUEST_METHOD'] == 'GET':
            return self.handle_get_login_form(env, start_response)
        elif env['REQUEST_METHOD'] == 'POST':
            return self.handle_submit_login_form(env, start_response)
        start_response('405 Method Not Allowed', [])
        return []

    def handle_get_login_form(self, env, start_response):
        start_response('200 OK', [])
        return ['''
                <html>
                <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" type="text/css" />
                <style>
                body {
                  background-color: grey;
                }
                div.jumbotron {
                  margin-top: 100px;
                }
                form {
                  margin-top: 50px;
                }
                </style>
                <body>
                <div class="container jumbotron">
                <h1>Sign in</h1>
                <form class="form-horizontal" role="form" method="POST" action="/login">
                  <div class="form-group">
                    <label for="username" class="col-sm-2 control-label">Username</label>
                    <div class="col-sm-10">
                      <input type="text" class="form-control" name="username" id="username" placeholder="username">
                    </div>
                  </div>
                  <div class="form-group">
                    <label for="password" class="col-sm-2 control-label">Password</label>
                    <div class="col-sm-10">
                      <input type="password" class="form-control" name="password" id="password" placeholder="Password">
                    </div>
                  </div>
                  <div class="form-group">
                    <div class="col-sm-offset-2 col-sm-10">
                      <button type="submit" class="btn btn-default">Sign in</button>
                    </div>
                  </div>
                </form>
                </div>
                </body>
                </html>
                ''']

    def handle_submit_login_form(self, env, start_response):
        form_data = parse_qs(env['wsgi.input'].read())
        env['HTTP_X_AUTH_USER'] = form_data['username'][0]
        env['HTTP_X_AUTH_KEY'] = form_data['password'][0]

        auth_info = {}

        def capture_auth_info(status, headers, *args, **kwargs):
            if not status.startswith('2'):
                start_response(status, headers, *args, **kwargs)
                return
            for k, value in headers:
                key = k.lower()
                if key in ('x-auth-token', 'x-storage-url'):
                    auth_info[key] = value
        env['REQUEST_METHOD'] = 'GET'
        env['PATH_INFO'] = '/auth/v1.0'
        resp = self.app(env, capture_auth_info)
        list(resp)
        if not auth_info:
            return resp
        start_response('303 See Other', [
            ('Location', auth_info['x-storage-url'].rstrip('/') + '/'),
            ('Set-Cookie', 'token=%s' % auth_info['x-auth-token']),
        ])
        return []

    def add_auth_from_cookie(self, env):
        raw_cookie = env['HTTP_COOKIE']
        cookies = {}
        for t in raw_cookie.split(','):
            k, v = t.split('=', 1)
            cookies[k] = v
        env['HTTP_X_AUTH_TOKEN'] = cookies['token']
        env['HTTP_X_WEB_MODE'] = 'true'

    def __call__(self, env, start_response):
        if env['PATH_INFO'].rstrip('/') == '/login':
            return self.handle_login(env, start_response)
        elif 'HTTP_COOKIE' in env:
            self.add_auth_from_cookie(env)
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def webauth_filter(app):
        return WebAuthMiddleware(app, conf)
    return webauth_filter
