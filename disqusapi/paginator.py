class Paginator(object):
    """
    Paginate through all entries:

    >>> paginator = Paginator(api.trends.listThreads, forum='disqus')
    >>> for result in paginator:
    >>>     print result

    Paginate only up to a number of entries:

    >>> for result in paginator(limit=500):
    >>>     print result
    """

    def __init__(self, endpoint, **params):
        self.endpoint = endpoint
        self.params = params

    def __iter__(self):
        for result in self():
            yield result

    def __call__(self, limit=None):
        params = self.params.copy()
        num = 0
        more = True
        while more and (not limit or num < limit):
            results = self.endpoint(**params)
            for result in results:
                if limit and num >= limit:
                    break
                num += 1
                yield result

            if results.cursor:
                more = results.cursor['more']
                params['cursor'] = results.cursor['id']
            else:
                more = False