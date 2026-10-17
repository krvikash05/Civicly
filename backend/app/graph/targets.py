"""Internal target guard shared by schema administration and repositories, not RBAC."""
import re
from uuid import RFC_4122, UUID, uuid4

CANONICAL_GRAPH = 'civicly_knowledge'
TEST_TARGET = re.compile(r'civicly_b(0[2-9]|1[0-9]|2[0-5])_test_([0-9a-f]{32})')


def is_disposable_graph(name: str) -> bool:
    if not isinstance(name, str) or (match := TEST_TARGET.fullmatch(name)) is None:
        return False
    token = UUID(hex=match[2])
    return token.version == 4 and token.variant == RFC_4122


def is_allowed_graph_target(name: str) -> bool:
    return isinstance(name, str) and (name == CANONICAL_GRAPH or is_disposable_graph(name))


def new_test_graph_name(milestone: int) -> str:
    if type(milestone) is not int or not 2 <= milestone <= 25:
        raise ValueError('Disposable schema/repository graphs require milestone 02–25')
    return f'civicly_b{milestone:02d}_test_{uuid4().hex}'
