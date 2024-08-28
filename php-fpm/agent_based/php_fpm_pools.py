#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2016             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# <<<php_fpm_pools>>>
# www dynamic active_processes 1
# www dynamic accepted_conn 726
# www dynamic listen_queue 0
# www dynamic start_since 79602
# www dynamic idle_processes 1
# www dynamic start_time 1545257568
# www dynamic slow_requests 0
# www dynamic max_active_processes 2
# www dynamic max_children_reached 0
# www dynamic max_listen_queue 0
# www dynamic total_processes 2


from typing import Any, Mapping
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

import time

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    check_levels,
    get_rate,
    get_value_store,
    GetRateError,
    register,
    render,
    Service,
)


Section = Mapping[str, Any]


def parse_php_fpm_pools(string_table: StringTable) -> Section:
    data = {}
    for line in string_table:
        if len(line) != 4:
            continue  # Skip unexpected lines
        pool_name, pm_type, metric, value = line
        item = '%s [%s]' % (pool_name, pm_type)
        if item not in data:
            data[item] = {}

        data[item][metric] = int(value)

    return data


register.agent_section(
    name='php_fpm_pools',
    parse_function=parse_php_fpm_pools,
)


def discover_php_fpm_pools(section: Section) -> DiscoveryResult:
    for item in section.keys():
        yield Service(item=item)


def check_php_fpm_pools(
    item: str,
    params: Mapping[str, Any],
    section: Section,
) -> CheckResult:
    if item not in section:
        return

    if params is None:
        params = {}

    data = dict(section[item])

    perfkeys = [
        'active_processes', 'idle_processes', 'max_active_processes',
        'max_children_reached', 'slow_requests', 'listen_queue',
        'max_listen_queue',
    ]

    # Add some more values, derived from the raw ones...
    this_time = int(time.time())
    for key in ['accepted_conn', 'max_children_reached', 'slow_requests']:
        try:
            per_sec = get_rate(
                get_value_store(),
                "php_fpm_status.%s" % key,
                this_time,
                data[key],
                raise_overflow=True
            )
        except GetRateError:
            pass
        else:
            data['%s_per_sec' % key] = per_sec
            perfkeys.append('%s_per_sec' % key)

    for key in perfkeys:
        yield from check_levels(
            value=data[key],
            metric_name=key,
            levels_lower=params.get(f'lower_{key}'),
            levels_upper=params.get(f'upper_{key}'),
            label=key.replace('_', ' ').title(),
            render_func=(
                render.timespan if key == 'start_since'
                else (lambda x: "%0.2f/s" % x) if key.endswith("_per_sec")
                else (lambda x: "%d" % x)
            ),
            notice_only=key not in (
                'active_processes',
                'idle_processes',
                'listen_queue',
                'start_since',
                'accepted_conn_per_sec',
            ),
        )


register.check_plugin(
    name='php_fpm_pools',
    service_name='PHP-FPM Pool %s Status',
    discovery_function=discover_php_fpm_pools,
    check_function=check_php_fpm_pools,
    check_ruleset_name='php_fpm_pools',
    check_default_parameters={},
)
