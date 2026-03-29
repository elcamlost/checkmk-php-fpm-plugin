PKG = php_fpm
CONTAINER = checkmk-${PKG}
IMAGE ?= checkmk/check-mk-raw:2.4.0-latest
MKP = $(shell ls ${PKG}*.mkp 2>/dev/null | head -1)

.DEFAULT: test
.PHONY: package test _docker_run _docker_stop _install _verify

package:
	bash package.sh

test: package _docker_run _install _verify _docker_stop

_docker_run:
	docker run --detach --rm --name=${CONTAINER} ${IMAGE}
	sleep 10

_docker_stop:
	docker stop -t 0 ${CONTAINER}

_install:
	docker cp ${MKP} ${CONTAINER}:/tmp/
	docker exec -u cmk ${CONTAINER} bash -l -c "mkp add /tmp/${MKP} && mkp enable ${PKG}"

_verify:
	docker exec -u cmk ${CONTAINER} bash -l -c "mkp list" | grep -q ${PKG}
