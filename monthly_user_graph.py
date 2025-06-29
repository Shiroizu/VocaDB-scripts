"""Generate a monthly comment count graph."""

from vdbpy.api.users import get_user_count_before
from vdbpy.utils.graph import get_monthly_graph

get_monthly_graph(get_user_count_before, "Monthly new users on VocaDB")
