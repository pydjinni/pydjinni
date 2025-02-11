grammar Idl;


idl              : load* namespaceContent* EOF;
load             : importDef | extern;
comment          : COMMENT+;
importDef        : IMPORT filepath;
extern           : EXTERN filepath;
filepath         : FILEPATH;
namespace        : comment? NAMESPACE nsIdentifier LBRACE namespaceContent* RBRACE;
namespaceContent : typeDecl | namespace;
typeDecl         : enum | flags | record | interface | namedFunction | errorDomain;
enum             : comment? identifier ASSIGN ENUM LBRACE item* RBRACE;
item             : comment? identifier SEMI;
flags            : comment? identifier ASSIGN FLAGS LBRACE flag* RBRACE;
flag             : comment? identifier modifier? SEMI;
modifier         : ASSIGN ID;
record           : comment? identifier ASSIGN RECORD targets LBRACE field* RBRACE deriving?;
field            : comment? identifier COLON typeRef SEMI;
typeRef          : dataType | function;
dataType         : nsIdentifier (LT (dataType COMMA)* dataType GT)? OPTIONAL?;
function         : (FUNCTION targets)? LPAREN ((parameter COMMA)* parameter)? RPAREN throwing? (ARROW typeRef)?;
throwing         : THROWS ( (typeRef COMMA)* typeRef)?;
targets          : TARGET*;
parameter        : identifier COLON typeRef;
deriving         : DERIVING LPAREN ((declaration COMMA)* declaration)? RPAREN;
declaration      : ID;
interface        : comment? identifier ASSIGN MAIN? INTERFACE targets LBRACE (method | prop)* RBRACE;
namedFunction    : comment? identifier ASSIGN function SEMI;
method           : comment? STATIC? CONST? ASYNC? identifier LPAREN ((parameter COMMA)* parameter)? RPAREN throwing? (ARROW typeRef)? SEMI;
errorDomain      : comment? identifier ASSIGN ERROR LBRACE errorCode* RBRACE;
errorCode        : comment? identifier (LPAREN ((parameter)* parameter)? RPAREN)? SEMI;
prop             : comment? PROPERTY identifier COLON typeRef SEMI;
identifier       : ID;
nsIdentifier     : NS_ID | ID;

IMPORT           : '@import';
EXTERN           : '@extern';
NAMESPACE        : 'namespace';
ENUM             : 'enum';
FLAGS            : 'flags';
STATIC           : 'static';
CONST            : 'const';
MAIN             : 'main';
INTERFACE        : 'interface';
RECORD           : 'record';
DERIVING         : 'deriving';
FUNCTION         : 'function';
PROPERTY         : 'property';
ASYNC            : 'async';
ERROR            : 'error';
THROWS           : 'throws';
ARROW            : '->';
OPTIONAL         : '?';
ASSIGN           : '=';
COLON            : ':';
LPAREN           : '(';
RPAREN           : ')';
LBRACE           : '{';
RBRACE           : '}';
GT               : '>';
LT               : '<';
SEMI             : ';';
COMMA            : ',';
DOT              : '.';
FILEPATH         : '"' .*? '"';
TARGET           : ('+' | '-') [a-z]+;
COMMENT          : '#' ~[\r\n]*;
WS               : [ \t\r\n]+ -> skip;


ID               : Letter LetterOrDigit*;
NS_ID            : (ID '.')* ID;

fragment LetterOrDigit : Letter | [0-9_];
fragment Letter        : [a-zA-Z];


