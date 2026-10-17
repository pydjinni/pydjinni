from pydjinni.parser.model.elements import (
    ClassType,
    CollectionType,
    Comment,
    Enum,
    ErrorDomain,
    Flags,
    Function,
    Interface,
    Namespace,
    Parameter,
    Record,
    Type,
    TypeReference,
)
lazy from pydjinni.parser.model.identifier import Identifier
lazy from pydjinni.parser.model.namespace_tuple import NamespaceTuple
lazy from pydjinni.position import Position


class NamedElementFactory:
    def create_namespace(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        types: tuple[Type, ...],
        namespaces: tuple[Namespace, ...],
    ) -> Namespace:
        return Namespace(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            types=types,
            namespaces=namespaces,
        )

    def create_error_domain(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        error_codes: tuple[ErrorDomain.ErrorCode, ...],
    ) -> ErrorDomain:
        return ErrorDomain(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            error_codes=error_codes,
        )

    def create_error_code(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        parameters: tuple[Parameter, ...],
    ) -> ErrorDomain.ErrorCode:
        return ErrorDomain.ErrorCode(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            parameters=parameters,
        )

    def create_function(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        target: ClassType.Target,
        return_reference: TypeReference | None,
        anonymous: bool,
        parameters: tuple[Parameter, ...],
        throwing: tuple[TypeReference, ...],
    ) -> Function:
        return Function(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            target=target,
            return_reference=return_reference,
            anonymous=anonymous,
            parameters=parameters,
            throwing=throwing,
        )

    def create_record(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        target: ClassType.Target,
        fields: tuple[Record.Field, ...],
        deriving: frozenset[Record.Deriving],
    ) -> Record:
        return Record(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            target=target,
            fields=fields,
            deriving=deriving,
        )

    def create_record_field(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        reference: TypeReference,
    ) -> Record.Field:
        return Record.Field(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            reference=reference,
        )

    def create_collection_type(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        params: tuple[str, ...],
    ) -> CollectionType:
        return CollectionType(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            params=params,
        )

    def create_interface(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        target: ClassType.Target,
        params: tuple[str, ...],
        methods: tuple[Interface.Method, ...],
        properties: tuple[Interface.Property, ...],
    ) -> Interface:
        return Interface(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            target=target,
            params=params,
            methods=methods,
            properties=properties,
        )

    def create_interface_method(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        static: bool,
        const: bool,
        return_reference: TypeReference | None,
        asynchronous: bool,
        parameters: tuple[Parameter, ...],
        throwing: tuple[TypeReference, ...],
    ) -> Interface.Method:
        return Interface.Method(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            static=static,
            const=const,
            return_reference=return_reference,
            asynchronous=asynchronous,
            parameters=parameters,
            throwing=throwing,
        )

    def create_interface_property(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        reference: TypeReference,
        readonly: bool,
    ) -> Interface.Property:
        return Interface.Property(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            reference=reference,
            readonly=readonly,
        )

    def create_parameter(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        reference: TypeReference,
    ) -> Parameter:
        return Parameter(
            position=position,
            namespace=namespace,
            name=name,
            reference=reference,
        )

    def create_enum(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        items: tuple[Enum.Item, ...],
    ) -> Enum:
        return Enum(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            items=items,
        )

    def create_enum_item(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
    ) -> Enum.Item:
        return Enum.Item(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
        )

    def create_flags(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        flags: tuple[Flags.Flag, ...],
    ) -> Flags:
        return Flags(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            flags=flags,
        )

    def create_flags_flag(
        self,
        position: Position,
        namespace: NamespaceTuple,
        name: Identifier,
        comment: Comment | None,
        modifier: Flags.Flag.Modifier | None,
    ) -> Flags.Flag:
        return Flags.Flag(
            position=position,
            namespace=namespace,
            name=name,
            comment=comment,
            modifier=modifier,
        )
