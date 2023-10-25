// Copyright 2023 jothepro
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

@interface OptionalTypesTests : XCTestCase

@property (nonatomic, strong) OptionalTypes * record;

@end

@implementation OptionalTypesTests

- (void)setUp {
    self.record = [OptionalTypes optionalTypesWithIntOptional: @42 stringOptional: @"optional"];
}

- (void)testOptionalTypes {
    OptionalTypes* returned_record = [Helper getOptionalTypes:self.record];

    XCTAssertEqualObjects(returned_record.intOptional, @42);
    XCTAssertEqualObjects(returned_record.stringOptional, @"optional");
}

- (void)testDescription {
    XCTAssertEqualObjects([self.record description], @"<OptionalTypes intOptional:42 stringOptional:optional>");
}

@end
