disqus-python
~~~~~~~~~~~~~

Let's start with installing the API:

	pip install disqus-python

Use the API by instantiating it, and then calling the method through dotted notation chaining::

	from disqusapi import DisqusAPI
	disqus = DisqusAPI(secret_key, public_key)
	for result in disqus.trends.listThreads():
	    print result

Parameters (including the ability to override version, api_secret, and format) are passed as keyword arguments to the resource call::

	disqus.posts.details(post=1, version='3.0')

Paginating through endpoints is easy as well::

	from disqusapi import Paginator
	paginator = Paginator(api.trends.listThreads, forum='disqus')
	for result in paginator:
	    print result

	# pull in a maximum of 500 results (this limit param differs from the endpoint's limit param)
	for result in paginator(limit=500):
	    print result

Documentation on all methods, as well as general API usage can be found at http://disqus.com/api/