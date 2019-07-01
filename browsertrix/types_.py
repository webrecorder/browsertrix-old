from asyncio import AbstractEventLoop
from typing import Any, Dict, List, Optional, Set, Type, Union

__all__ = [
    'AnyDict',
    'AnyDictList',
    'EnvType',
    'EnvValue',
    'Loop',
    'Number',
    'OptionalAny',
    'OptionalAnyDict',
    'OptionalBool',
    'OptionalLoop',
    'OptionalNumber',
    'OptionalSetStr',
    'OptionalStr',
    'OptionalStrList',
]

AnyDict = Dict[Any, Any]
AnyDictList = List[AnyDict]
Loop = AbstractEventLoop
Number = Union[int, float]
EnvValue = Union[str, bool, dict, Number]
EnvType = Type[EnvValue]

OptionalAny = Optional[Any]
OptionalAnyDict = Optional[AnyDict]
OptionalBool = Optional[bool]
OptionalLoop = Optional[Loop]
OptionalNumber = Optional[Number]
OptionalSetStr = Optional[Set[str]]
OptionalStr = Optional[str]
OptionalStrList = Optional[List[str]]
