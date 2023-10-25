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

@interface FunctionTests : XCTestCase

@end

@implementation FunctionTests


- (void)testNamedFunction {
    [Helper namedFunction: ^ BOOL (int32_t input) {
        return input == 42;
    }];
}

- (void)testAnonymousFunction {
    [Helper anonymousFunction: ^ BOOL (int32_t input) {
        return input == 42;
    }];
}

- (void)testCppNamedFunction {
    BOOL (^block) (int32_t)  = [Helper cppNamedFunction];
    BOOL result = block(42);
    XCTAssertTrue(result);
}

- (void)testCppAnonymousFunction {
    BOOL (^block) (int32_t)  = [Helper cppAnonymousFunction];
    BOOL result = block(42);
    XCTAssertTrue(result);
}

- (void)testCppFunctionThrowingException {
    void(^block)() = [Helper cppFunctionThrowingException];
    XCTAssertThrowsSpecificNamed(block(), NSException, @"shit hit the fan");
};


@end
