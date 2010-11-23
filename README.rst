disqus-python
~~~~~~~~~~~~~

Let's start with installing the API:

	pip install disqus-python

Use the API by instantiating it, and then calling the method through dotted notation chaining::

	from disqusapi import DisqusAPI
	disqus = DisqusAPI(secret_key)
	disqus.trends.listThreads()

Parameters (including the ability to override version, api_secret, and format) are passed as keyword arguments to the resource call::

	disqus.posts.details(post=1, version='3.0')

Documentation on all methods, as well as general API usage can be found at http://disqus.com/api/