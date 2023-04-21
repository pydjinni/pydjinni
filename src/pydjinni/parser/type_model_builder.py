from pydantic import create_model, BaseModel


class TypeModelBuilder:
    """
    Create the BaseModel for (external) type validation from all loaded generator modules
    """

    def __init__(self, model_base: type[BaseModel]):
        self._model_base = model_base
        self._models: dict[str, type[BaseModel]] = {}

    def add_field(self, field_name: str, model: type(BaseModel)):
        self._models[field_name] = model

    def build(self):
        field_kwargs = {key: (model, None) for key, model in self._models.items()}
        return create_model(
            self._model_base.__name__,
            __base__=self._model_base,
            **field_kwargs
        )
