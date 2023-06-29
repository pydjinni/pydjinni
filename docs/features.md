# Features

## Namespaces { .new-badge }

The Interface file can now be structured with sub-namespaces. Consider the following example:

```djinni
namespace foo {
    bar = record {}
}
```

This will define a record inside a namespace. The namespace is applied on top of the package/namespace defined by
the configuration.

## Types

### Optional types { .new-badge }

Suffixing a type with a `?` marks it as optional. Optional values may be null.

```djinni
foo = record {
    bar: i32?;
}
```

## Record

### Deriving

For record types, Haskell-style "deriving" declarations are supported to generate some common methods.
This way for example equality and order comparators or a method for giving a string representation of the record
can be added. Not all features may be available in all target languages. 
Consult the [Reference](deriving.md) for a full list of available declarations.

```djinni
foo = record {
    bar: i32;
} deriving (str, eq, ord)
```

## Interface 

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

### Properties { .new-badge }

When designing an interface, the `property` descriptor can be used to define values that support a mechanism of
notification when the value has changed.

Consider the following example:

```djinni
foo = interface {
    property bar: i8;
}
```

=== "C++"

    - If the interface is targeting C++, a public getter and a protected setter for the property will be generated.
    - If the interface is **not** targeting C++, a public getter and a notify method 
    `on_bar_changed(std::function<void(Bar)> callback)` will be generated to allow the observation of the property.

=== "Java"

    - If the interface is targeting Java, a public getter and a protected setter for the property will be generated.
    - If the interface is **not** targeting C++, a public getter and a callback method will be defined.

=== "Objective-C"

    A Objective-C property is defined, that can be observed with Key-Value Observing (KVO).

=== "C#"

    A C# property is defined.
