# Pygments

The `pydjinni` package automatically defines an [entry-point](https://pygments.org/docs/plugins/#entrypoints){ target=_blank}
for a primitive custom Pygments Lexer for IDL files.

Once installed, it is automatically registered in Pygments for syntax-highlighting IDL files:

```shell
 pygmentize -l djinni -f html test.djinni
```

The Lexer is also used for rendering IDL files in this documentation.
