from typing import TypeVar
from pydantic import BaseModel

# 제네릭 State 타입
StateType = TypeVar('StateType', bound=BaseModel)

# LangGraph 노드 반환 타입 재수출
from langgraph.graph.schema import NodeOutput
