#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

register_rule(
    "agents/" + _("Agent Plugins"),
    "agent_config:php_fpm_pools",
    Alternative(
        title = _("Php-fpm Pools Status"),
        help = _("This will deploy the agent plugin <tt>php_fpm_pools</tt> "
                 "for checking php-fpm pools. <b>Note:</b> If you want "
                 "to configure several sockets to look into "
                 "then simply create several rules. In this ruleset "
                 "<b>all</b> matching rules "
                 "are being executed, not only the first one. "),
        style = "dropdown",
        elements = [
            Dictionary(
                title = _("Deploy the Php-fpm-pools plugin"),
                elements = [
                   ("interval", Age(
                        title = _("Run asynchronously"),
                        label = _("Interval for collecting data"),
                        default_value = 3600
                   )),
                   ("sockets",
                     ListOf(
                        CascadingDropdown(
                            title=_("Socket"),
                            help= _("Enter socket parameters"),
                            style="dropdown",
                            choices=[
                                ("tcp",
                                 _("TCPSocket"),
                                 Tuple(elements=[
                                    Hostname(
                                     title=_("Host Address"),
                                     default_value="localhost",
                                     allow_empty=False,
                                    ),
                                    Integer(
                                     title=_("TCP Port Number"),
                                     minvalue=1,
                                     maxvalue=65535,
                                     default_value="9000",
                                    ),
                                 ]),
                                ),
                                ("unix",
                                 _("UnixSocket"),
                                 Tuple(elements=[
                                    TextAscii(
                                     title=_("File Path"),
                                     size = 80,
                                     regex = "^/[^ \t]+$",
                                     regex_error = _("UnixSocket path must begin with <tt>/</tt> and must not contain spaces."),
                                     allow_empty=False,
                                    ),
                                    TextAscii(
                                     title=_("Pool Status Path"),
                                     regex = "^/[^ \t]+$",
                                     regex_error = _("Pool status path must begin with <tt>/</tt> and must not contain spaces."),
                                     default_value="/fpm_status",
                                     allow_empty=False,
                                    ),
                                 ]),
                                ),
                            ],
                        ), 
                     ),
                   ),
                ],
                optional_keys = [ 'interval' ],
            ),
            FixedValue(None, title = _("Do not deploy the Php-fpm-pools plugin"), totext = _("(disabled)") ),
        ]
    ),
)
