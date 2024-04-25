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
#import "TSTCalculator.h"

@interface PlatformImplementation : NSObject <TSTPlatformInterface>
@end

@interface NoParametersNoReturnCallbackImpl : NSObject <TSTNoParametersNoReturnCallback>
    @property BOOL callbackInvoked;
@end

@interface InterfaceTests : XCTestCase

@property (nonatomic, strong) TSTCalculator * calculator;

@end

@implementation InterfaceTests

- (void)setUp {
    self.calculator = [TSTCalculator getInstance];
}

- (void)testCalculator {
    int8_t result = [self.calculator add:40 b:2];
    XCTAssertEqual(result, 42, @"The calculator has returned an unexpected value");
}

- (void)testPlatformImplementation {
    PlatformImplementation* implementation = [[PlatformImplementation alloc] init];
    int8_t result = [self.calculator getPlatformValue:implementation];
    XCTAssertEqual(result, 5, @"The result from the Objective-C implementation was not as expected");
}

- (void)testMethodNoParametersNoReturn {
    [self.calculator noParametersNoReturn];
}

- (void)testMethodThrowingException {
    XCTAssertThrowsSpecificNamed([self.calculator throwingException], NSException, @"shit hit the fan");
}

- (void)testNoParametersNoReturnCallback {
    NoParametersNoReturnCallbackImpl* callback = [[NoParametersNoReturnCallbackImpl alloc] init];
    [self.calculator noParametersNoReturnCallback:callback];
    XCTAssertTrue(callback.callbackInvoked, @"Callback was not invoked");
}

@end

@implementation PlatformImplementation
- (int8_t)getValue {
    return 5;
}
@end

@implementation NoParametersNoReturnCallbackImpl
-(id)init {
    if (self = [super init])  {
        self.callbackInvoked = NO;
    }
    return self;
}
- (void)invoke {
    self.callbackInvoked = YES;
}
@end
