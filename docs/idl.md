# IDL

The Interface Definition Language (IDL) is used to define the interface between C++ and 
the host language.

## PEG grammar

The grammar of the IDL is defined in [Parsing Expression Grammars](https://bford.info/pub/lang/peg.pdf){ target=_blank }
(PEG) notation. The grammar below is the actual definition used by the `arpeggio` parser.

{{ idl_grammar("src/pydjinni/parser/grammar/idl.cleanpeg") }}

The grammar has one odd characteristic, that should be mentioned: Comments are actually part of the syntax and are 
parsed and processed by the parser, because they have a semantic meaning to the generator.
This means that comments are only valid above an identifier that they describe.

The original Djinni parser would allow comments everywhere but discard them if they could not be linked to an 
identifier.
In PyDjinni, the parser will not accept comments in unexpected locations, in order to more clearly communicate the 
semantic meaning of comments to the user.

## Examples

```djinni
my_cool_enum = enum {
    option1;
    option2;
    option3;
}

# test comment
# this is a test comment with a list:
# * first
# * second
my_flags = flags {
    # flag comment
    flag1;
    flag2;
    flag3;
    no_flags = none;
    all_flags = all;
    more = all;
}

foo = record {
    # comment
    id: i16;
    info: i16;
}

my_cpp_interface = main interface +cpp {
    # comment
    method_returning_nothing(
        value: i16,
        foo: i16
    );
    method_returning_some_type(key: i8) -> foo;
    static get_version() -> i8;
}
```
