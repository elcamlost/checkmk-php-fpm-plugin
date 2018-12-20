def php_fpm_pools_upper_bounds(title, warn, crit, unit = None):
    spec_type = {
        int: Integer,
        float: Float,
        str: TextAscii
    }
    return Tuple(
        title = title,
        elements = [
            spec_type[type(warn)](title = _("Warning at"), unit = unit, default_value = warn),
            spec_type[type(warn)](title = _("Critical at"), unit = unit, default_value = crit),
        ]
    )

def php_fpm_pools_lower_bounds(title, warn, crit, unit=None):
    spec_type = {
        int: Integer,
        float: Float,
        str: TextAscii
    }
    return Tuple(
        title = title,
        elements = [
            spec_type[type(warn)](title = _("Warning below"), unit = unit, default_value = warn),
            spec_type[type(warn)](title = _("Critical below"), unit = unit, default_value = crit),
        ]
    )
