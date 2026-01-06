ENV_FILE := .env
include $(ENV_FILE)
export
# REMOTE_URL    # where `deploy` uploads to
# LOCAL_URL     # where `deploy-local` is served at, via local static webserver
# LOCAL_BASEDIR # where `deploy-local` copies to

.phony: render deploy deploy-local view view-local

LOCAL_HTML := ff-dashboard.html
FTP_BASE := ftp://${WEBSITE_FTP_URL}/recipes
FTP_AUTH := --user ${WEBSITE_FTP_USERNAME}:${WEBSITE_FTP_PASSWORD}
FTP_FLAGS := -s --ftp-ssl --ssl-reqd --insecure
CURL_UPLOAD := curl ${FTP_FLAGS} ${FTP_AUTH} -T

run:
	$(MAKE) render
	$(MAKE) deploy-local
	$(MAKE) view-local-deploy

render:
	python3 firefox-tool.py render

clean:
	rm -f tmp

deploy:
	@${CURL_UPLOAD} $< ${FTP_BASE}/index.html

deploy-local:
	cp ${LOCAL_HTML} ${LOCAL_BASEDIR}/index.html
	cp dashboard.css ${LOCAL_BASEDIR}/dashboard.css
	cp dashboard.js ${LOCAL_BASEDIR}/dashboard.js

view:
	firefox ${REMOTE_URL}/index.html

view-local:
	firefox ${LOCAL_HTML}

view-local-deploy:
	firefox ${LOCAL_URL}/index.html
