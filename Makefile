PKG = php_fpm
CONTAINER = checkmk-${PKG}
IMAGE = checkmk/check-mk-raw:1.6.0p11
DIRS = $(shell ls -d ${PWD}/php-fpm/*/)
MKP = $(shell docker exec -u cmk checkmk-php_fpm bash -c "ls -1 ~/*mkp")

.DEFAULT: php_fpm
.PHONY: _docker_run _docker_stop _copy_files _pack php_fpm

_docker_run:
	docker run --detach --rm --name=${CONTAINER} ${IMAGE}
	sleep 10

_docker_stop:
	docker stop -t 0 checkmk-${PKG}

_copy_files:
	for dir in $$(ls -d $$PWD/php-fpm/*/); do docker cp $$dir ${CONTAINER}:/omd/sites/cmk/local/share/check_mk/; done

_copy_info:
	docker cp ${PWD}/php-fpm/info ${CONTAINER}:/omd/sites/cmk/var/check_mk/packages/${PKG}

_pack:
	docker exec -u cmk ${CONTAINER} bash -l -c "cd ~ && mkp pack ${PKG}"
	docker cp ${CONTAINER}:${MKP} ./

php_fpm: _docker_run _copy_files _copy_info _docker_stop


