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

## Record



## Interface 

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
