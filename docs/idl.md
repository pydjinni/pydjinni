# Interface Definition

The Interface Definition Language (IDL) is used to define the interface between C++ and 
the host language.

## Built-In Types

PyDjinni comes with a set of built-in data types. Consult the [Types](types.md) reference for a full list of all 
available types.

### Optional types { .new-badge }

Suffixing a type with a `?` marks it as optional. Optional values may be null.

```djinni
foo = record {
    bar: i32?;
}
```

## Enums

```pydjinni
foo = enum {
    option1;
    option2;
    option3;
}
```


## Flags

```pydjinni
bar = flags {
    flag1;
    flag2;
    flag3;
    no_flags = none;
    all_flags = all;
}
```

## Record

Records are pure data value objects, that combine multiple fields into a data class.

```pydjinni
data = record {
    id: i32;
    info: string;
    store: set<string>;
    hash: map<string, i32>;
}
```

### Extensions

To support extra fields and/or methods, a record can be "extended" in any language.
To extend a record in a language, you can add a language target flag after the record tag.
The generated type will have a Base suffix, and you should create a derived type without the suffix that extends 
the record type.

The derived type must be constructible in the same way as the Base type.
Interfaces will always use the derived type.

### Deriving

For record types, Haskell-style "deriving" declarations are supported to generate some common methods.
This way for example equality and order comparators or a method for giving a string representation of the record
can be added. Not all features may be available in all target languages. 
Consult the [Deriving Reference](deriving.md) for a full list of available declarations.

```djinni
foo = record {
    bar: i32;
} deriving (str, eq, ord)
```

## Interface

Interfaces are objects with defined methods to call (in C++, passed by `shared_ptr`).
PyDjinni produces code allowing an interface implemented in C++ to be transparently used from Objective-C or Java 
and vice versa.

```pydjinni
# This interface will be implemented in C++ 
# and can be called from any language.
my_cpp_interface = interface +cpp {
    method_returning_nothing(value: i32);
    method_returning_some_type(key: string) -> data;
    static get_version() -> i32;
}

# This interface will be implemented 
# in Java or Objective-C and can be called from C++.
my_client_interface = interface -cpp {
    log_string(str: string) -> bool;
}
```

### Special Methods for C++ only

`+cpp` interfaces (implementable only in C++) can have methods flagged with the special keywords `const` and `static`
which have special effects in C++:

```pydjinni
special_methods = interface +cpp { 
    const accessor_method(); 
    static factory_method(); 
}
```

- `const` methods will be declared as `const` in C++, though this cannot be enforced on callers in other languages, 
  which lack this feature.
- `static` methods will become a `static` method of the C++ class, which can be called from other languages without an 
  object. This is often useful for factory methods to act as a cross-language constructor.

### Exception Handling

When an interface implemented in C++ throws a `std::exception`, it will be translated to a `java.lang.RuntimeException`
in Java and an `NSException` in Objective-C. The `what()` message will be translated as well.

### Main Interface { .new-badge }

Usually a PyDjinni library will have one or more entrypoints, in the form of an `interface` with a `static` constructor.
When using the library from Java, it is vital to ensure that the underlying native JNI library is loaded before 
calling the constructor.

Usually this requires a `System.loadLibrary("FooBar");` call ahead of time.

To automate the native library loading, any C++ interface can be marked as `main`:

```djinni
foo = main interface +cpp {
   static get_instance(): foo
}
```

Given that the name of the native library is configured in the `generator.java.native_lib` property, a static
initialization block is added to the interface, ensuring that the native library is loaded automatically.

If no interface is marked `main`, the underlying loader can be initialized manually. 
It is named `<native_lib>Loader` and lives in the `native_lib` sub-package:

```java
class Main {
    static {
        new foo.bar.native_lib.FooBarLoader()
    }
}
```

## Functions { .new-badge }

Functions can be passed to and returned from interface methods.
They are represented by [`std::function`](https://en.cppreference.com/w/cpp/utility/functional/function){target=blank} in C++, 
[`@FunctionalInterface`](https://docs.oracle.com/javase/8/docs/api/java/lang/FunctionalInterface.html){target=blank} in Java and 
[`blocks`](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/WorkingwithBlocks/WorkingwithBlocks.html){target=blank} in Objective-C.

Functions can either be defined like a type, or can be defined inline where they are needed as anonymous functions:


```djinni
named_func = function (input: i32) -> bool;

foo = interface {
    register_callback(callback: named_func);
    register_anonymous_callback(callback: (input: i32) -> bool);
}
```

There is a short and a long form for defining functions.
The long form allows target flags to be added in order to optimize the generated code:

```djinni
callback = function -cpp (input: i32) -> bool;
```

The short form doesn't allow for code optimization, but in return is a lot more brief:
```djinni
callback = (input: i32) -> bool;
```

## Namespaces { .new-badge }

The interface file can be structured with namespaces:

```djinni
namespace foo {
    bar = record {}
}
```

The specified namespace is appended to the base namespace that is defined in the generator configuration.

## Comments { .new-badge }

Comments starting with `#` are converted to documentation comments in the generated interfaces.

[CommonMark](https://commonmark.org) flavored Markdown can be used to format the text.

The following special commands are available:

{{ markdown_special_commands() }}

Both JavaDoc or Doxygen style commands can be used: `@deprecated`, `\deprecated`.


## ANTLR grammar

The grammar of the IDL is defined with ANTRL. The grammar below is the actual definition used by the parser:

{{ idl_grammar("src/pydjinni/parser/grammar/Idl.g4") }}


