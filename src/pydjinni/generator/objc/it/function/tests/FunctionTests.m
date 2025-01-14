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
#import "TSTHelper.h"

@interface FunctionTests : XCTestCase

@end

@implementation FunctionTests


- (void)testNamedFunction {
    [TSTHelper namedFunction: ^ BOOL (NSString * input) {
        return [input isEqualToString: @"foo"];
    }];
}

- (void)testAnonymousFunction {
    [TSTHelper anonymousFunction: ^ BOOL (NSString * input) {
        return [input isEqualToString: @"foo"];
    }];
}

- (void)testCppNamedFunction {
    BOOL (^block) (NSString *)  = [TSTHelper cppNamedFunction];
    BOOL result = block(@"foo");
    XCTAssertTrue(result);
}

- (void)testCppAnonymousFunction {
    BOOL (^block) (NSString *)  = [TSTHelper cppAnonymousFunction];
    BOOL result = block(@"foo");
    XCTAssertTrue(result);
}

- (void)testCppFunctionThrowingException {
    void(^block)() = [TSTHelper cppFunctionThrowingException];
    XCTAssertThrowsSpecificNamed(block(), NSException, @"shit hit the fan");
};

- (void)testAnonymousFunctionPassingRecord {
    [TSTHelper anonymousFunctionPassingRecord: ^ BOOL (TSTFoo * foo) {
        return foo.a == 32;
    }];
}


@end
