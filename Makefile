PKG = php_fpm
CONTAINER = checkmk-${PKG}
IMAGE ?= checkmk/check-mk-raw:2.4.0-latest
MKP = $(shell ls ${PKG}*.mkp 2>/dev/null | head -1)

.DEFAULT: unit_test
.PHONY: package test

package:
	python3 package.py

unit_test:
	.venv/bin/pytest

test: package
	docker run --detach --rm --name=${CONTAINER} ${IMAGE}
	sleep 10
	docker cp ${MKP} ${CONTAINER}:/tmp/ && \
	docker exec -u cmk ${CONTAINER} bash -l -c "mkp add /tmp/${MKP} && mkp enable ${PKG}" && \
	docker exec -u cmk ${CONTAINER} bash -l -c "mkp list" | grep -q ${PKG}; \
	EXIT=$$?; docker stop -t 0 ${CONTAINER}; exit $$EXIT
