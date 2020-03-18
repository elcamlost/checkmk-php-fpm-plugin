# Colors:
#
#                   red
#  magenta                       orange
#            11 12 13 14 15 16
#         46                   21
#         45                   22
#   blue  44                   23  yellow
#         43                   24
#         42                   25
#         41                   26
#            36 35 34 33 32 31
#     cyan                       yellow-green
#                  green
#
# Special colors:
# 51  gray
# 52  brown 1
# 53  brown 2
#
# For a new metric_info you have to choose a color. No more hex-codes are needed!
# Instead you can choose a number of the above color ring and a letter 'a' or 'b
# where 'a' represents the basic color and 'b' is a nuance/shading of the basic color.
# Both number and letter must be declared!
#
# Example:
# "color" : "23/a" (basic color yellow)
# "color" : "23/b" (nuance of color yellow)
#
# As an alternative you can call indexed_color with a color index and the maximum
# number of colors you will need to generate a color. This function tries to return
# high contrast colors for "close" indices, so the colors of idx 1 and idx 2 may
# have stronger contrast than the colors at idx 3 and idx 10.

metric_info["accepted_conn_per_sec"] = {
    "title" : _("the number of requests per second"),
    "unit"  : "",
    "color" : "31/a",
}

graph_info.append({
    "title"   : _("Requests per second"),
    "metrics" : [
        ( "accepted_conn_per_sec", "area" ),
    ],
})

metric_info["max_children_reached_per_sec"] = {
    "title" : _("the number of max_children reached per second"),
    "unit"  : "",
    "color" : "14/a",
}

graph_info.append({
    "title"   : _("Max children reached per second"),
    "metrics" : [
        ( "max_children_reached_per_sec", "area" ),
    ],
})

metric_info["slow_requests_per_sec"] = {
    "title" : _("the number of slow requests per second"),
    "unit"  : "",
    "color" : "12/a",
}

graph_info.append({
    "title"   : _("Slow requests per second"),
    "metrics" : [
        ( "slow_requests_per_sec", "area" ),
    ],
})

metric_info["listen_queue"] = {
    "title" : _("the number of request in the queue of pending connections"),
    "unit"  : "",
    "color" : "41/a",
}

metric_info["max_listen_queue"] = {
    "title" : _("the maximum number of requests in the queue of pending connections since FPM has started"),
    "unit"  : "",
    "color" : "51/a",
}

graph_info.append({
    "title"   : _("Listen queue"),
    "metrics" : [
        ( "listen_queue", "stack" ),
        ( "max_listen_queue", "line" ),
    ],
})

metric_info["idle_processes"] = {
    "title" : _("the number of idle processes"),
    "unit"  : "",
    "color" : "51/b",
}

metric_info["active_processes"] = {
    "title" : _("the number of active processes"),
    "unit"  : "",
    "color" : "33/a",
}

metric_info["max_active_processes"] = {
    "title" : _("the maximum number of active processes since FPM has started"),
    "unit"  : "",
    "color" : "13/a",
}

graph_info.append({
    "title"   : _("Processes"),
    "metrics" : [
        ( "active_processes", "area" ),
        ( "idle_processes", "stack" ),
        ( "max_active_processes", "line" ),
    ],
})

metric_info["max_children_reached"] = {
    "title" : _("max_children_reached"),
    "unit"  : "",
    "color" : "14/a",
}

metric_info["slow_requests"] = {
    "title" : _("slow_requests"),
    "unit"  : "",
    "color" : "15/a",
}

