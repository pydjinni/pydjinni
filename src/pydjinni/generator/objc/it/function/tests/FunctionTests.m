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
    void(^block)(NSError**) = [TSTHelper cppFunctionThrowingException];
    NSError* error;
    block(&error);
    XCTAssertNotNil(error);
    XCTAssertEqual(error.code, 0);
    XCTAssertEqualObjects(error.localizedDescription, @"shit hit the fan");
}

- (void)testCppFunctionThrowingBarError {
    void(^block)(NSError**) = [TSTHelper cppFunctionThrowingBarError];
    NSError* error;
    block(&error);
    XCTAssertNotNil(error);
    XCTAssertEqual(error.domain, TSTBarDomain);
    XCTAssertEqual(error.code, TSTBarBadStuff);
}

- (void)testAnonymousFunctionPassingRecord {
    [TSTHelper anonymousFunctionPassingRecord: ^ BOOL (TSTFoo * foo) {
        return foo.a == 32;
    }];
}

- (void)testFunctionParameterThrowing {
    NSError* error;
    [TSTHelper functionParameterThrowing:^(NSError** functionError){
        *functionError = [NSError errorWithDomain:NSCocoaErrorDomain code: NSFileNoSuchFileError userInfo:@{
            NSLocalizedDescriptionKey: @"unexpected error from host",
            NSFilePathErrorKey: @"some.file"
        }];
    } error: &error];
    XCTAssertNotNil(error);
    XCTAssertEqual(error.domain, NSCocoaErrorDomain);
    XCTAssertEqual(error.code, NSFileNoSuchFileError);
    XCTAssertEqualObjects(error.localizedDescription, @"unexpected error from host");
    XCTAssertEqualObjects(error.userInfo[NSFilePathErrorKey], @"some.file");
}


@end
