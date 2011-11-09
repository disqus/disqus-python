import binascii
import hashlib
import hmac
import urllib
import urlparse

def get_normalized_params(params):
    """
    Given a list of (k, v) parameters, returns
    a sorted, encoded normalized param
    """
    return urllib.urlencode(sorted(params))

def get_normalized_request_string(method, url, nonce, params, ext='', body_hash=None):
    """
    Returns a normalized request string as described iN OAuth2 MAC spec.

    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00#section-3.3.1
    """
    urlparts = urlparse.urlparse(url)
    if urlparts.query:
        norm_url = '%s?%s' % (urlparts.path, urlparts.query)
    elif params:
        norm_url = '%s?%s' % (urlparts.path, get_normalized_params(params))
    else:
        norm_url = urlparts.path

    if not body_hash:
        body_hash = get_body_hash(params)

    port = urlparts.port
    if not port:
        assert urlparts.scheme in ('http', 'https')

        if urlparts.scheme == 'http':
            port = 80
        elif urlparts.scheme == 'https':
            port = 443

    output = [nonce, method.upper(), norm_url, urlparts.hostname, port, body_hash, ext, '']

    return '\n'.join(map(str, output))

def get_body_hash(params):
    """
    Returns BASE64 ( HASH (text) ) as described in OAuth2 MAC spec.

    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00#section-3.2
    """
    norm_params = get_normalized_params(params)

    return binascii.b2a_base64(hashlib.sha1(norm_params).digest())[:-1]

def get_mac_signature(api_secret, norm_request_string):
    """
    Returns HMAC-SHA1 (api secret, normalized request string)
    """
    hashed = hmac.new(str(api_secret), norm_request_string, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]