from cmk.graphing.v1 import Title, graphs, metrics

PHP_FPM_UNIT_NUMBER = metrics.Unit(metrics.DecimalNotation(''))
PHP_FPM_UNIT_PER_SECOND = metrics.Unit(metrics.DecimalNotation('/s'))

php_fpm_metric_accepted_conn_per_sec = metrics.Metric(
    name="accepted_conn_per_sec",
    title=Title("the number of requests per second"),
    unit=PHP_FPM_UNIT_PER_SECOND,
    color=metrics.Color.YELLOW,
)


php_fpm_metric_max_children_reached_per_sec = metrics.Metric(
    name="max_children_reached_per_sec",
    title=Title("the number of max_children reached per second"),
    unit=PHP_FPM_UNIT_PER_SECOND,
    color=metrics.Color.RED,
)


php_fpm_metric_slow_requests_per_sec = metrics.Metric(
    name="slow_requests_per_sec",
    title=Title("the number of slow requests per second"),
    unit=PHP_FPM_UNIT_PER_SECOND,
    color=metrics.Color.DARK_PINK,
)

php_fpm_metric_listen_queue = metrics.Metric(
    name="listen_queue",
    title=Title("the number of request in the queue of pending connections"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.CYAN,
)

php_fpm_metric_max_listen_queue = metrics.Metric(
    name="max_listen_queue",
    title=Title("the maximum number of requests in the queue of pending connections since FPM has started"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.GRAY,
)


php_fpm_metric_idle_processes = metrics.Metric(
    name="idle_processes",
    title=Title("the number of idle processes"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.BROWN,
)

php_fpm_metric_active_processes = metrics.Metric(
    name="active_processes",
    title=Title("the number of active processes"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.BLUE,
)

php_fpm_metric_max_active_processes = metrics.Metric(
    name="max_active_processes",
    title=Title("the maximum number of active processes since FPM has started"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.DARK_PURPLE,
)


php_fpm_metric_max_children_reached = metrics.Metric(
    name="max_children_reached",
    title=Title("max_children_reached"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.ORANGE,
)

php_fpm_metric_slow_requests = metrics.Metric(
    name="slow_requests",
    title=Title("slow_requests"),
    unit=PHP_FPM_UNIT_NUMBER,
    color=metrics.Color.DARK_RED,
)

php_fpm_graph_rps = graphs.Graph(
    name="rps",
    title=Title("Requests per second"),
    compound_lines=["accepted_conn_per_sec"],
)


php_fpm_graph_max_children_reached_ps = graphs.Graph(
    name="max_children_reached_ps",
    title=Title("Max children reached per second"),
    compound_lines=["max_children_reached_per_sec"],
)

php_fpm_graph_slow_rps = graphs.Graph(
    name="slow_rps",
    title=Title("Slow requests per second"),
    compound_lines=["slow_requests_per_sec"],
)

php_fpm_graph_listen_queue = graphs.Graph(
    name="listen_queue",
    title=Title("Listen queue"),
    simple_lines=["max_listen_queue"],
    compound_lines=["listen_queue"],
)

php_fpm_graph_processes = graphs.Graph(
    name="processes",
    title=Title("Processes"),
    simple_lines=["max_active_processes"],
    compound_lines=["active_processes", "idle_processes"],
)
