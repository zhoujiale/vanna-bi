
from vanna.core.registry import ToolRegistry
from vanna.tools import VisualizeDataTool
from app.vanna.database import db_tool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool, SaveTextMemoryTool


def get_tools():
    """获取工具注册"""

    tools = ToolRegistry()
    tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])
    tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])
    return tools

tools = get_tools()