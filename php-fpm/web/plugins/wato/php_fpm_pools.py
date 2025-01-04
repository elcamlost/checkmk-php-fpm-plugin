#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    Float,
    TextAscii,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)


def _item_spec_php_fpm_pools():
    return TextAscii(title=_("PHP-FPM Pool name"),
                     help=_("A string-combination of pool name and pm strategy, e.g. example_com:ondemand."))


def _integer_levels(unit):
    return [
        Integer(title=_("Warning at"), unit=_(unit)),
        Integer(title=_("Critical at"), unit=_(unit)),
    ]


def _float_levels(unit):
    return [
        Float(title=_("Warning at"), unit=_(unit)),
        Float(title=_("Critical at"), unit=_(unit)),
    ]


def _parameter_valuespec_php_fpm_pools():
    return Dictionary(elements=[
        ("requests_per_sec",
         Tuple(
             title=_("Request per Second"),
             help=_("Upper levels for the current number of requests handled "
                    "by the fpm pool per second."),
             elements=_integer_levels("requests/second"),
         )),
        ("idle_processes",
         Tuple(
             title=_("Idle Processes"),
             help=_("Lower levels for the number of idle processes"),
             elements=_integer_levels("processes"),
         )),
        ("max_children_reached",
         Tuple(
             title=_("Max children reached"),
             help=_("Upper levels for the number of times the maximum number "
                    "of children has been reached <b>since the start of "
                    "php-fpm</b>."),
             elements=_integer_levels("times"),
         )),
        ("max_children_reached_per_sec",
         Tuple(
             title=_("Max children reached per second"),
             help=_("Upper levels for the number of times the maximum number "
                    "of children has been reached per second since the last "
                    "check"),
             elements=_float_levels("times/second"),
         )),
        ("slow_requests",
         Tuple(
             title=_("Slow Requests"),
             help=_("Upper levels for the number of slow requests <b>since the "
                    "start of php-fpm</b>"),
             elements=_integer_levels("requests"),
         )),
        ("slow_requests_per_sec",
         Tuple(
             title=_("Slow Requests per second"),
             help=_("Upper levels for the number of slow requests <b>per "
                    "second</b> since the last check"),
             elements=_integer_levels("requests/second"),
         )),
        ("listen_queue",
         Tuple(
             title=_("Listen Queue"),
             help=_("Upper levels for the number of pending requests on the "
                    "listen queue, which is limited by the "
                    "<code>pm.backlog</code> option"),
             elements=_integer_levels("requests"),
         )),
        ("max_listen_queue",
         Tuple(
             title=_("Max Listen Queue"),
             help=_("Upper levels for the maximum number of pending requests "
                    "on the listen queue <b>since the start of php-fpm</b>."),
             elements=_integer_levels("requests"),
         )),
    ])


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="php_fpm_pools",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_php_fpm_pools,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_php_fpm_pools,
        title=lambda: _("PHP-FPM Pools"),
    ))
