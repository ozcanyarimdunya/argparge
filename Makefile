.PHONY: help

help:
	@echo "help        : Show this help message"
	@echo "serve-docs  : Run documentation server"
	@echo "build-docs  : Build mkdocs"
	@echo "install     : Install dependencies"
	@echo "gh-deploy   : Deploy to GitHub pages"
	@echo "publish-pypi: Deploy to pypi"

serve-docs:
	@poetry run mkdocs serve

build-docs:
	@poetry run mkdocs build

install:
	@poetry install

gh-deploy:
	@poetry run mkdocs gh-deploy --clean --force

publish-pypi:
	@poetry build
	@poetry config pypi-token.pypi $(PYPI_TOKEN)
	@poetry publish --dry-run
	@poetry publish
	@rm -rf dist
	@rm -rf *.egg-info
