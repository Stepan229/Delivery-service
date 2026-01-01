from dataclasses import asdict



def dataclass_to_pydantic(dataclass_obj, pydantic_model_class):
    return pydantic_model_class(**asdict(dataclass_obj))