dev:
	pip install -r dev-requirements.txt

lint:
	flake8 disqusapi/

test:
	nosetests

clean:
	rm -rf *.egg-info *.egg dist/ build/

release:
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: dev lint test clean release
