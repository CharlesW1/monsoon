import logging


def _parse_cmdline_args_safe(cmdline_args):
    """Drop-in replacement for lcu_driver.utils.parse_cmdline_args.

    The bundled lcu-driver (3.0.0a1) parses the League client command line with
    ``key, value = cmdline_arg[2:].split('=')``, which assumes each argument
    contains exactly one ``=``. Newer Riot clients pass arguments whose values
    contain ``=`` (e.g. ``--riotgamesapi-settings=<base64...=>``), so the split
    yields more than two parts and raises ``ValueError: too many values to
    unpack``. That crashes the connection thread and Monsoon never connects.

    Splitting on the first ``=`` only keeps the whole value intact.
    """
    parsed = {}
    for cmdline_arg in cmdline_args:
        if len(cmdline_arg) > 0 and '=' in cmdline_arg:
            key, value = cmdline_arg[2:].split('=', 1)
            parsed[key] = value
    return parsed


def apply_lcu_cmdline_patch():
    """Patch lcu-driver so it can parse modern League client command lines.

    Safe to call more than once. connection.py binds the function by name
    (``from .utils import parse_cmdline_args``), so patch that reference too.
    """
    try:
        import lcu_driver.utils as _utils
        import lcu_driver.connection as _connection
        _utils.parse_cmdline_args = _parse_cmdline_args_safe
        _connection.parse_cmdline_args = _parse_cmdline_args_safe
        logging.debug("Applied lcu-driver cmdline parser patch")
    except Exception:
        logging.exception("Failed to apply lcu-driver cmdline parser patch")
