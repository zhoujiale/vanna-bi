from vanna.integrations.chromadb import ChromaAgentMemory


def get_agent_memory():
    """获取智能体记忆"""
    return ChromaAgentMemory(
    collection_name="vanna_memory",
    persist_directory="./chroma_db"
)

agent_memory = get_agent_memory()
