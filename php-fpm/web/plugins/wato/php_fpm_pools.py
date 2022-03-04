#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
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


def _parameter_valuespec_php_fpm_pools():
    return Dictionary(elements=[
        ("requests_per_sec",
         Tuple(
             title=_("Request per Second"),
             help=_("You can configure upper thresholds for the currently rps "
                    "handled by the fpm pool."),
             elements=[
                 Integer(title=_("Warning at"), unit=_("connections")),
                 Integer(title=_("Critical at"), unit=_("connections"))
             ],
         ))
    ],)


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="php_fpm_pools",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_php_fpm_pools,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_php_fpm_pools,
        title=lambda: _("PHP-FPM Pools"),
    ))
