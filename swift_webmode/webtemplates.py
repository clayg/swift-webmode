from swift.common.swob import wsgify, Request, Response, HTTPSeeOther
from swift.common.utils import split_path, json

from swift.proxy.controllers.base import get_account_info, get_container_info

from jinja2 import Template


class WebTemplateMiddleware(object):

    def __init__(self, app, conf):
        self.app = app
        self.conf = conf

    def get_template(self, req, account, container=None):
        template_key = 'web-listing-template'
        if container:
            info = get_container_info(req.environ, self.app)
        else:
            info = get_account_info(req.environ, self.app)
        template_path = info['meta'].get(template_key)
        if not template_path:
            return
        if ':' not in template_path and not template_path.startswith('/'):
            template_path = '/v1/%s/%s' % (account, template_path)
        headers = {
            'x-auth-token': req.headers.get('x-auth-token'),
        }
        template_req = Request.blank(template_path, method='GET',
                                     headers=headers)
        template_resp = template_req.get_response(self.app)
        return Template(template_resp.body)

    @wsgify
    def __call__(self, req):
        account = None
        try:
            (version, account, container, obj) = \
                split_path(req.path_info, 2, 4, True)
        except ValueError:
            pass
        if not account or not req.headers.get('x-web-mode'):
            return req.get_response(self.app)
        if not obj:
            req.query_string = 'format=json'
        resp = req.get_response(self.app)
        if resp.content_type == 'application/json':
            listing = json.loads(resp.body)
            template = self.get_template(req, account, container)
            if template:
                ctx = {
                    'account': account,
                    'container': container,
                    'listing': listing,
                }
                if container:
                    index = [o for o in listing if o['name'] == 'index.html']
                    if index:
                        headers = {'Location': '/v1/%s/%s/index.html' %
                                   (account, container)}
                        return HTTPSeeOther(headers=headers)
                return Response(body=template.render(**ctx))
            else:
                index = [o for o in listing if o['name'] == 'index.html']
                if index:
                    headers = {'Location': '/v1/%s/%s/index.html' %
                               (account, container)}
                    return HTTPSeeOther(headers=headers)
        return resp


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def webtemplate_filter(app):
        return WebTemplateMiddleware(app, conf)
    return webtemplate_filter
