import click

def parse_max_videos(ctx, param, value):
    """
    Click callback to handle --max-videos option.
    Allows an integer or 'all'.
    Default when not provided: 10.
    """
    if value is None:
        return 10  # default
    if isinstance(value, str) and value.lower() == "all":
        return None  # None means fetch all
    try:
        ivalue = int(value)
        if ivalue < 1:
            raise click.BadParameter("Must be a positive integer or 'all'.")
        return ivalue
    except ValueError:
        raise click.BadParameter("Must be a positive integer or 'all'.")
