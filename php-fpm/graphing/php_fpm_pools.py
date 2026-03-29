from cmk.graphing.v1 import Title, graphs, metrics

PHP_FPM_UNIT_NUMBER = metrics.Unit(metrics.DecimalNotation(""))
PHP_FPM_UNIT_PER_SECOND = metrics.Unit(metrics.DecimalNotation("/s"))

metric_php_fpm_accepted_conn_per_sec = metrics.Metric(
    name="accepted_conn_per_sec",
    title=Title("the number of requests per second"),
    unit=PHP_FPM_UNIT_PER_SECOND,
    color=metrics.Color.YELLOW,
)


metric_php_fpm_max_children_reached_per_sec = metrics.Metric(
    name="max_children_reached_per_sec",
    title=Title("the number of max_children reached per second"),
    unit=PHP_FPM_UNIT_PER_SECOND,
    color=metrics.Color.RED,
)


metric_php_fpm_slow_requests_per_sec = metrics.Metric(
    name="slow_requests_per_sec",
    title=Title("the number of slow requests per second"),
    unit=PHP_FPM_UNIT_PER_SECOND,
    color=metrics.Color.DARK_PINK,
)

metric_php_fpm_listen_queue = metrics.Metric(
    name="listen_queue",
    title=Title("the number of request in the queue of pending connections"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.CYAN,
)

metric_php_fpm_max_listen_queue = metrics.Metric(
    name="max_listen_queue",
    title=Title("the maximum number of requests in the queue of pending connections since FPM has started"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.GRAY,
)


metric_php_fpm_idle_processes = metrics.Metric(
    name="idle_processes",
    title=Title("the number of idle processes"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.BROWN,
)

metric_php_fpm_active_processes = metrics.Metric(
    name="active_processes",
    title=Title("the number of active processes"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.BLUE,
)

metric_php_fpm_max_active_processes = metrics.Metric(
    name="max_active_processes",
    title=Title("the maximum number of active processes since FPM has started"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.DARK_PURPLE,
)


metric_php_fpm_max_children_reached = metrics.Metric(
    name="max_children_reached",
    title=Title("how many time max_children has been reached since pool start"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.ORANGE,
)

metric_php_fpm_slow_requests = metrics.Metric(
    name="slow_requests",
    title=Title("the number of slow requests"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.DARK_RED,
)

graph_php_fpm_rps = graphs.Graph(
    name="rps",
    title=Title("Requests per second"),
    compound_lines=["accepted_conn_per_sec"],
)


graph_php_fpm_max_children_reached_ps = graphs.Graph(
    name="max_children_reached_ps",
    title=Title("Max children reached per second"),
    compound_lines=["max_children_reached_per_sec"],
)

graph_php_fpm_slow_rps = graphs.Graph(
    name="slow_rps",
    title=Title("Slow requests per second"),
    compound_lines=["slow_requests_per_sec"],
)

graph_php_fpm_listen_queue = graphs.Graph(
    name="listen_queue",
    title=Title("Listen queue"),
    simple_lines=["max_listen_queue"],
    compound_lines=["listen_queue"],
)

graph_php_fpm_processes = graphs.Graph(
    name="processes",
    title=Title("Processes"),
    simple_lines=["max_active_processes"],
    compound_lines=["active_processes", "idle_processes"],
)
