Getting Started
===============

 1. Install swift_webmode

   * `python setup.py develop`

 1. Add webauth and webtemplate sections to proxy config::

    ```
    [filter:webauth]
    use = egg:swift_webmode#webauth

    [filter:webtemplates]
    use = egg:swift_webmode#webtemplates

    [pipeline:main]
    pipeline = proxy-logging healthcheck cache webauth tempauth webtemplates proxy-logging proxy-server
    ```
    
 1. Restart Proxy

   * `swift-init proxy restart`

 1. Upload source

   * `cd <swift-webmode>/examples`
   * `swift upload .src *.js *.tmpl`

 1. Set Account & Container metadata

   * `swift post -m 'web-listing-template: .src/account.tmpl`
   * `swift post -m 'web-listing-template: .src/slideshow.tmpl' pics`
   * `cd <my-pics>`
   * `swift upload pics *`
