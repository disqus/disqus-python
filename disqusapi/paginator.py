class Paginator(object):
    """
    Paginate through all entries:

    >>> paginator = Paginator(api, 'trends.listThreads', forum='disqus')
    >>> for result in paginator:
    >>>     print result

    Paginate only up to a number of entries:

    >>> for result in paginator(limit=500):
    >>>     print result
    """

    def __init__(self, *args, **params):
        from disqusapi import InterfaceNotDefined
        if len(args) == 2:
            self.method = args[0]
            self.endpoint = args[1]
        elif len(args) == 1:
            self.method = None
            self.endpoint = args[0]
        else:
            raise InterfaceNotDefined
        self.params = params

    def __iter__(self):
        for result in self():
            yield result

    def __call__(self, limit=None):
        params = self.params.copy()
        num = 0
        more = True
        while more and (not limit or num < limit):
            if self.method:
                results = self.method(self.endpoint, **params)
            else:
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
