// Copyright 2023 - 2024 jothepro
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
#import "Helper.h"

@interface NestedTypeTests : XCTestCase

@property (nonatomic, strong) ParentType * record;

@end

@implementation NestedTypeTests

- (void)setUp {
    self.record = [ParentType parentTypeWithNested:[NestedType nestedTypeWithA: 42 b: @[@[@1, @2], @[@3, @4]]]];
}

- (void)testNestedType {
    ParentType* returned_record = [Helper getNestedType:self.record];
    XCTAssertEqual(returned_record.nested.a, 42);
}

- (void)testDescription {
    XCTAssertEqualObjects([self.record description], @"<ParentType nested:<NestedType a:42 b:(\n"
                                                     @"        (\n"
                                                     @"        1,\n"
                                                     @"        2\n"
                                                     @"    ),\n"
                                                     @"        (\n"
                                                     @"        3,\n"
                                                     @"        4\n"
                                                     @"    )\n"
                                                     @")>>");
}

@end
