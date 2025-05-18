PKG = php_fpm
CONTAINER = checkmk-${PKG}
IMAGE = checkmk/check-mk-raw:2.4.0p1
DIRS = agent_based checkman graphing rulesets info
MKP = $(shell docker exec -u cmk checkmk-php_fpm bash -c "ls -1 /omd/sites/cmk/var/check_mk/packages_local/*mkp")

.DEFAULT: php_fpm
.PHONY: _docker_run _docker_stop _copy_files _pack _copy_mkp php_fpm

_docker_run:
	docker run --detach --rm --name=${CONTAINER} ${IMAGE}
	sleep 10

_docker_stop:
	docker stop -t 0 checkmk-${PKG}

_copy_files:
	docker exec ${CONTAINER} mkdir -p /omd/sites/cmk/local/lib/python3/cmk_addons/plugins/${PKG}
	for dir in ${DIRS}; do \
	    docker cp php-fpm/$$dir ${CONTAINER}:/omd/sites/cmk/local/lib/python3/cmk_addons/plugins/${PKG}/$$dir; \
	done
	docker exec ${CONTAINER} chown -R cmk /omd/sites/cmk/local/lib/python3/cmk_addons/plugins/${PKG}
	docker cp php-fpm/agents ${CONTAINER}:/omd/sites/cmk/local/share/check_mk/; \
	docker exec ${CONTAINER} chown -R cmk /omd/sites/cmk/local/share/check_mk/agents/plugins/

_pack:
	docker exec -u cmk ${CONTAINER} bash -l -c "mkp package /omd/sites/cmk/local/lib/python3/cmk_addons/plugins/${PKG}/info"

_copy_mkp:
	docker cp ${CONTAINER}:${MKP} ./

php_fpm: _docker_run _copy_files _pack _copy_mkp _docker_stop
