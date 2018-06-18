.PHONY: activate install test watch package deploy
activate:
	virtualenv -p python3 ./.venv
	echo "Now run: source ./.venv/bin/activate"
install:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt
test:
	nosetests src
watch:
	nosetests src --with-watch
clean:
	rm -rf build
build:
	cp -R src build
	cp -R certs build/certs
	cp -R schemas build/schemas
	pip install -r requirements.txt --target=./build
package:
	aws cloudformation package --template-file ./template.yaml --s3-bucket deploymentbucket-emxyh72p1x99 --output-template-file template_packaged.yaml
deploy:
	cat template_params.txt | xargs aws cloudformation deploy --template-file ./template_packaged.yaml --capabilities CAPABILITY_IAM
	head -1 template_params.txt | xargs aws cloudformation describe-stacks
