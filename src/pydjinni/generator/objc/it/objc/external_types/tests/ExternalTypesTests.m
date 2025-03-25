// Copyright 2025 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#import <XCTest/XCTest.h>
#import "TSTMainInterface.h"
#import "EXTFooEnumType.h"
#import "EXTFlagsType.h"
#import "EXTRecordType.h"
#import "EXTFunctionType.h"

@interface ExternalTypesTests : XCTestCase
@end

@implementation ExternalTypesTests

- (void)testUsingExternalTypes {
    BOOL result = [TSTMainInterface
                   useExternalTypes: EXTFooEnumTypeA
                         flagsParam: EXTFlagsTypeA
                        recordParam: [EXTRecordType recordTypeWithA: 4 b: 2 c: @"foo"]
                      functionParam: ^{ return YES; }];
    XCTAssertTrue(result);
}

@end
