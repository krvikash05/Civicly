"""Pre-dispatch model READ validation; no tools, graph writes or argument rewriting."""
from jsonschema import Draft202012Validator, FormatChecker
from app.mcp.policy import Request


class SelectionInputError(ValueError):
    """Static public feedback only; never echo untrusted argument values."""


def validate_read(selection, context):
    if selection.action != 'READ':
        return
    tool = next((t for t in context.get('catalog', []) if t['name'] == selection.tool_name), None)
    if tool is None:
        raise SelectionInputError('READ_TOOL_NOT_DISCOVERED: choose an exact catalog name.')
    shape = tool.get('input_schema')
    if shape is None:
        shape = context.get('tool_schemas', {}).get(tool.get('input_schema_ref'))
    if not isinstance(shape, dict):
        raise SelectionInputError('READ_SCHEMA_UNAVAILABLE: pause instead of inventing arguments.')
    args = selection.arguments
    try:
        Draft202012Validator(shape, format_checker=FormatChecker()).validate(args)
        if any(k in args for k in ('graph', 'graphName', 'query', '_context', 'tool')):
            raise ValueError('host scope')
        if selection.tool_name.startswith('official::'):
            # Reuse the broker's cross-field rules, including template/as_of and registry types.
            Request.model_validate({**args, 'tool': selection.tool_name.removeprefix('official::')})
    except Exception:
        raise SelectionInputError('READ_ARGUMENT_SCHEMA: use the selected tool schema exactly; official node reads require template=node and id, with no as_of or sample_size.') from None
    # A known asset cannot also be a Location. Do not infer type from ID spelling.
    state = context.get('state', {})
    if args.get('location_id') in state.get('asset_ids', []):
        raise SelectionInputError('READ_LOCATION_TYPE: location_id must identify a Location, not an affected asset. Retrieve its actual location through approved graph reads, or pause if unavailable.')
    cutoff = state.get('as_of')
    if cutoff:
        from app.graph.schema import timestamp
        try:
            if any(timestamp(args[k]) > timestamp(cutoff) for k in ('as_of', 'to_time') if args.get(k)):
                raise ValueError('future cutoff')
            if args.get('from_time') and args.get('to_time') and timestamp(args['from_time']) > timestamp(args['to_time']):
                raise ValueError('reversed interval')
        except ValueError:
            raise SelectionInputError('READ_TIME_WINDOW: use a valid ordered interval ending no later than state.as_of.') from None
