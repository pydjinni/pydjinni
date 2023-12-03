# Generated from Idl.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .IdlParser import IdlParser
else:
    from IdlParser import IdlParser

# This class defines a complete generic visitor for a parse tree produced by IdlParser.

class IdlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by IdlParser#idl.
    def visitIdl(self, ctx:IdlParser.IdlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#comment.
    def visitComment(self, ctx:IdlParser.CommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#importDef.
    def visitImportDef(self, ctx:IdlParser.ImportDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#extern.
    def visitExtern(self, ctx:IdlParser.ExternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#filepath.
    def visitFilepath(self, ctx:IdlParser.FilepathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namespace.
    def visitNamespace(self, ctx:IdlParser.NamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namespaceBegin.
    def visitNamespaceBegin(self, ctx:IdlParser.NamespaceBeginContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namespaceEnd.
    def visitNamespaceEnd(self, ctx:IdlParser.NamespaceEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#typeDecl.
    def visitTypeDecl(self, ctx:IdlParser.TypeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#enum.
    def visitEnum(self, ctx:IdlParser.EnumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#item.
    def visitItem(self, ctx:IdlParser.ItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#flags.
    def visitFlags(self, ctx:IdlParser.FlagsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#flag.
    def visitFlag(self, ctx:IdlParser.FlagContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#modifier.
    def visitModifier(self, ctx:IdlParser.ModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#record.
    def visitRecord(self, ctx:IdlParser.RecordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#field.
    def visitField(self, ctx:IdlParser.FieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#typeRef.
    def visitTypeRef(self, ctx:IdlParser.TypeRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#dataType.
    def visitDataType(self, ctx:IdlParser.DataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#function.
    def visitFunction(self, ctx:IdlParser.FunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#targets.
    def visitTargets(self, ctx:IdlParser.TargetsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#parameter.
    def visitParameter(self, ctx:IdlParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#deriving.
    def visitDeriving(self, ctx:IdlParser.DerivingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#declaration.
    def visitDeclaration(self, ctx:IdlParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#interface.
    def visitInterface(self, ctx:IdlParser.InterfaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#namedFunction.
    def visitNamedFunction(self, ctx:IdlParser.NamedFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#method.
    def visitMethod(self, ctx:IdlParser.MethodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#prop.
    def visitProp(self, ctx:IdlParser.PropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#identifier.
    def visitIdentifier(self, ctx:IdlParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by IdlParser#nsIdentifier.
    def visitNsIdentifier(self, ctx:IdlParser.NsIdentifierContext):
        return self.visitChildren(ctx)



del IdlParser