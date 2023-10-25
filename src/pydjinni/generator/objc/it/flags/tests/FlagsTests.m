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

@interface FlagsTests : XCTestCase
@end

@implementation FlagsTests

- (void)testFlags {
    XCTAssertEqual([Helper getFlag:ExampleFlagsA], ExampleFlagsA, @"Returned Flag does not match input");
}

- (void)testAllFlags {
    XCTAssertEqual([Helper getAllFlag:ExampleFlagsAll], ExampleFlagsAll, @"Returned Flag does not match input");
}

- (void)testNoneFlags {
    XCTAssertEqual([Helper getNoneFlag:ExampleFlagsNone], ExampleFlagsNone, @"Returned Flag does not match input");
}


@end
