PKG = php_fpm
CONTAINER = checkmk-${PKG}
IMAGE = checkmk/check-mk-raw:2.2.0p37
DIRS = agents checkman web
MKP = $(shell docker exec -u cmk checkmk-php_fpm bash -c "ls -1 ~/*mkp")

.DEFAULT: php_fpm
.PHONY: _docker_run _docker_stop _copy_files _pack _copy_mkp php_fpm

_docker_run:
	docker run --detach --rm --name=${CONTAINER} ${IMAGE}
	sleep 10

_docker_stop:
	docker stop -t 0 checkmk-${PKG}

_copy_files:
	for dir in ${DIRS}; do docker cp php-fpm/$$dir ${CONTAINER}:/omd/sites/cmk/local/share/check_mk/; done
	docker cp php-fpm/agent_based ${CONTAINER}:/omd/sites/cmk/local/lib/check_mk/base/plugins/

_copy_info:
	docker cp ${PWD}/php-fpm/info ${CONTAINER}:/omd/sites/cmk/var/check_mk/packages/${PKG}

_pack:
	docker exec -u cmk ${CONTAINER} bash -l -c "cd ~ && mkp pack ${PKG}"

_copy_mkp:
	docker cp ${CONTAINER}:${MKP} ./

php_fpm: _docker_run _copy_files _copy_info _pack _copy_mkp _docker_stop
