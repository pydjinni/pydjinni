/*#
Copyright 2023 jothepro

        Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#*/
//> extends "base.jinja2"

//> block content
@implementation {{ type_def.objc.name }}

- (nonnull instancetype){{ type_def.objc.init }}
    /*>- for field in type_def.fields -*/
        {{ (" " ~ field.objc.name if not loop.first) ~ ":" }}({{ field.objc.type_decl}}){{ field.objc.name }}
    /*>- endfor */ {
    if(self = [super init]) {
        /*> for field in type_def.fields */
            _{{ field.objc.name }} = {{ field.objc.name }};
        /*> endfor */
    }
    return self;
}

+ (nonnull instancetype){{ type_def.objc.convenience_init }}
    /*>- for field in type_def.fields -*/
        {{ (" " ~ field.objc.name if not loop.first) ~ ":" }}({{ field.objc.type_decl}}){{ field.objc.name }}
    /*>- endfor */ {
    return [({{ type_def.objc.name }}*)[self alloc] {{ type_def.objc.init }}
    /*>- for field in type_def.fields -*/
        {{ (" " ~ field.objc.name if not loop.first) ~ ":" }}{{ field.objc.name }}
    /*>- endfor -*/
    ];
}

//> if 'eq' in type_def.deriving:
- (BOOL)isEqual:(id)other
{
    if (![other isKindOfClass:[{{ type_def.objc.name }} class]]) {
        return NO;
    }
    {{ type_def.objc.name }} *typedOther = ({{ type_def.objc.name }} *)other;
    return
    /*>- for field in type_def.fields */
{{ (" " * 11 if not loop.first else " ") ~ field.objc.equals ~ (";" if loop.last else " &&") }}
    /*> endfor */
}

- (NSUInteger)hash
{
    return NSStringFromClass([self class]).hash ^
    //> for field in type_def.fields:
           {{ field.objc.hash_code ~ (";" if loop.last else " ^") }}
    //> endfor
}
//> endif

//> if 'ord' in type_def.deriving:
- (NSComparisonResult)compare:({{ type_def.objc.name }} *)other
{
    NSComparisonResult tempResult;
    //> for field in type_def.fields:
    //> if field.type_ref.type_def.objc.typename == field.type_ref.type_def.objc.boxed:
    tempResult = [self.{{ field.objc.name }} compare:other.{{ field.objc.name }}];
    //> else:
    if (self.{{ field.objc.name }} < other.{{ field.objc.name }}) {
        tempResult = NSOrderedAscending;
    } else if (self.{{ field.objc.name }} > other.{{ field.objc.name }}) {
        tempResult = NSOrderedDescending;
    } else {
        tempResult = NSOrderedSame;
    }
    //> endif
    if (tempResult != NSOrderedSame) {
        return tempResult;
    }
    //> endfor
    return NSOrderedSame;
}
//> endif

//> if config.string_serialization:
- (NSString *)description {
    return [NSString stringWithFormat:@"<%@
    /*>- for field in type_def.fields -*/
        {{ " " ~ field.objc.name }}:%@
    /*>- endfor -*/
    >", self.class
    /*>- for field in type_def.fields -*/
        /*>- if field.deprecated -*/
        {{ " PYDJINNI_DISABLE_DEPRECATED_WARNINGS " }}
        /*>- endif -*/
        /*>- if field.type_ref.type_def.name == "bool" -*/
            , self.{{ field.objc.name }} ? @"YES" : @"NO"
        /*>- elif not field.type_ref.type_def.objc.pointer and not field.type_ref.optional -*/
            , @(self.{{ field.objc.name }})
        /*>- else -*/
            , self.{{ field.objc.name }}
        /*>- endif -*/
        /*>- if field.deprecated -*/
        {{ " PYDJINNI_ENABLE_WARNINGS " }}
        /*>- endif -*/
    /*>- endfor -*/
    ];
}
//> endif
@end
//> endblock
