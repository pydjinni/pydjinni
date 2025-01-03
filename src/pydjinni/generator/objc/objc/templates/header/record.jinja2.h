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
/*> if type_def.objc.base_type */
@class {{ type_def.objc.derived_name }};
/*> endif */
//? type_def.objc.comment : type_def.objc.comment | comment
//? type_def.objc.attributes : type_def.objc.attributes | join('\n')
@interface {{ type_def.objc.name }} : NSObject
- (nonnull instancetype){{ type_def.objc.init }}
    /*>- for field in type_def.fields -*/
        {{ (" " ~ field.objc.name if not loop.first) ~ ":" }}({{ (field.objc.annotation ~ " ") if field.objc.annotation }}{{ field.objc.type_decl }}){{ field.objc.name }}
    /*>- endfor -*/;
+ (nonnull instancetype){{ type_def.objc.convenience_init }}
    /*>- for field in type_def.fields -*/
        {{ (" " ~ field.objc.name if not loop.first) ~ ":" }}({{ (field.objc.annotation ~ " ") if field.objc.annotation }}{{field.objc.type_decl }}){{ field.objc.name }}
    /*>- endfor -*/;
//> for field in type_def.fields:
//? field.objc.comment : field.objc.comment | comment
@property (nonatomic, readonly{{ ", " ~ field.objc.annotation if field.objc.annotation }}) {{ field.objc.type_decl }} {{ field.objc.name ~ (field.objc.attributes | concat(prefix='\n')) }};
//> endfor
//> if 'ord' in type_def.deriving
- (NSComparisonResult)compare:(nonnull {{ type_def.objc.name }} *)other;
//> endif
@end
//> endblock
