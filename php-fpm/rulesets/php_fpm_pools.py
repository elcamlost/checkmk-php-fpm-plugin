#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import (
    Help,
    Label,
    Title,
)

from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    Integer,
    migrate_to_integer_simple_levels
    Float,
    migrate_to_float_simple_levels,
    String,
)

from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    HostCondition,
    Topic,
)

def _parameter_valuespec_php_fpm_pools():
    return Dictionary(elements=[
        ("requests_per_sec": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Request per Second"),
            help_text=Help("Upper levels for the current number of requests handled "
                           "by the fpm pool per second."),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Float(unit_symbol="requests/second"),
            migrate=migrate_to_float_simple_levels,
        ))),
        ("idle_processes": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Idle Processes"),
            help_text=Help("Lower levels for the number of idle processes"),
            level_direction=LevelDirection.LOWER,
            form_spec_template=Integer(unit_symbol="processes"),
            migrate=migrate_to_integer_simple_levels,
        ))),
        ("max_children_reached": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Max children reached"),
            help_text=Help("Upper levels for the number of times the maximum number "
                           "of children has been reached <b>since the start of php-fpm</b>."),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Integer(unit_symbol="times"),
            migrate=migrate_to_integer_simple_levels,
        ))),
        ("max_children_reached_per_sec": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Max children reached per second"),
            help_text=Help("Upper levels for the number of times the maximum number "
                           "of children has been reached per second since the last check"),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Float(unit_symbol="times/second"),
            migrate=migrate_to_float_simple_levels,
        ))),
        ("slow_requests": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Slow Requests"),
            help_text=Help("Upper levels for the number of slow requests <b>since the "
                           "start of php-fpm</b>"),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Integer(unit_symbol="requests"),
            migrate=migrate_to_integer_simple_levels,
        ))),
        ("slow_requests_per_sec": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Slow Requests per second"),
            help_text=Help("Upper levels for the number of slow requests <b>per "
                           "second</b> since the last check"),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Float(unit_symbol="requests/second"),
            migrate=migrate_to_float_simple_levels,
            ))),
        ("listen_queue": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Listen Queue"),
            help_text=Help("Upper levels for the number of pending requests on the "
                           "listen queue, which is limited by the "
                           "<code>pm.backlog</code> option"),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Integer(unit_symbol="requests"),
            migrate=migrate_to_integer_simple_levels,
        ))),
        ("max_listen_queue": DictElement(
            parameter_form=SimpleLevels[int](
            title=Title("Max Listen Queue"),
            help_text=Help("Upper levels for the maximum number of pending requests "
                           "on the listen queue <b>since the start of php-fpm</b>."),
            level_direction=LevelDirection.UPPER,
            form_spec_template=Integer(unit_symbol="requests"),
            migrate=migrate_to_integer_simple_levels,
        ))),
    ])

rule_spec_php_fpm = CheckParameters(
    name="php_fpm_pools",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_valuespec_php_fpm_pools,
    title=Title("PHP-FPM Pools"),
    condition=HostAndItemCondition(
        item_title=Title("Instance"),
        item_form=String(),
    ),
)
