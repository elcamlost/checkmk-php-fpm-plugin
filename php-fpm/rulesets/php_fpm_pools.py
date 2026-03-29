#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import (
    Help,
    Title,
)
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    Integer,
    LevelDirection,
    SimpleLevels,
    String,
    migrate_to_float_simple_levels,
    migrate_to_integer_simple_levels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic,
)


def _parameter_valuespec_php_fpm_pools():
    return Dictionary(
        elements={
            "accepted_conn_per_sec": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Request per Second"),
                    help_text=Help(
                        "Upper levels for the current number of requests handled by the fpm pool per second."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="requests/second"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=DefaultValue((10.0, 30.0)),
                )
            ),
            "idle_processes": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Idle Processes"),
                    help_text=Help("Lower levels for the number of idle processes"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Integer(unit_symbol="processes"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((1, 0)),
                )
            ),
            "max_children_reached": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Max children reached"),
                    help_text=Help(
                        "Upper levels for the number of times the maximum number "
                        "of children has been reached <b>since the start of php-fpm</b>."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="times"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((1, 3)),
                )
            ),
            "max_children_reached_per_sec": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Max children reached per second"),
                    help_text=Help(
                        "Upper levels for the number of times the maximum number "
                        "of children has been reached per second since the last check"
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="times/second"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=DefaultValue((1.0, 3.0)),
                )
            ),
            "slow_requests": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Slow Requests"),
                    help_text=Help("Upper levels for the number of slow requests <b>since the start of php-fpm</b>"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="requests"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((1, 3)),
                )
            ),
            "slow_requests_per_sec": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Slow Requests per second"),
                    help_text=Help(
                        "Upper levels for the number of slow requests <b>per second</b> since the last check"
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="requests/second"),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=DefaultValue((1.0, 3.0)),
                )
            ),
            "listen_queue": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Listen Queue"),
                    help_text=Help(
                        "Upper levels for the number of pending requests on the "
                        "listen queue, which is limited by the "
                        "<code>pm.backlog</code> option"
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="requests"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((255, 511)),
                )
            ),
            "max_listen_queue": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Max Listen Queue"),
                    help_text=Help(
                        "Upper levels for the maximum number of pending requests "
                        "on the listen queue <b>since the start of php-fpm</b>."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="requests"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((255, 511)),
                )
            ),
            "memory_total_rss": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Total Worker Memory (RSS)"),
                    help_text=Help("Upper levels for the total RSS memory used by all worker processes in the pool."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="bytes"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((512 * 1024 * 1024, 1024 * 1024 * 1024)),
                )
            ),
            "memory_avg_rss": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Average Worker Memory (RSS)"),
                    help_text=Help("Upper levels for the average RSS memory per worker process in the pool."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="bytes"),
                    migrate=migrate_to_integer_simple_levels,
                    prefill_fixed_levels=DefaultValue((128 * 1024 * 1024, 256 * 1024 * 1024)),
                )
            ),
        }
    )


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
