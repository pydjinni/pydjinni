// Copyright 2024 jothepro
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
#import "TSTAsynchronous.h"

// Runs the NSRunLoop for a short time to allow the async methods to dispatch a callback.
#define SYNC_WAIT [[NSRunLoop mainRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.05]]

@interface MultiplyCallbackImpl : NSObject <TSTMultiplyCallback>
@end

@interface NoParametersNoReturnCallbackImpl : NSObject <TSTNoParametersNoReturnCallback>
@end

@interface AsyncTests : XCTestCase

@property (nonatomic, strong) TSTAsynchronous * asynchronous;

@end

@implementation AsyncTests

- (void)setUp {
    [TSTAsynchronous getInstance: ^(TSTAsynchronous * result){
        self.asynchronous = result;
    }];
    SYNC_WAIT;
}

- (void)testAsyncMethodCall {
    __block int32_t result;
    [self.asynchronous add:40 b:2 completion: ^(int32_t outcome){
        result = outcome;
    }];
    SYNC_WAIT;
    XCTAssertEqual(result, 42, @"The completion handler has returned an unexpected value");
}

- (void)testNoParametersNoReturnCall {
    __block BOOL completionCalled = NO;
    [self.asynchronous noParametersNoReturn: ^(){
        completionCalled = YES;
    }];
    SYNC_WAIT;
    XCTAssertEqual(completionCalled, YES, @"The completion handler was not called");
}

- (void)testAsyncCallback {
    MultiplyCallbackImpl* callback = [[MultiplyCallbackImpl alloc] init];
    __block int32_t result;
    [self.asynchronous multiplyCallback:callback completion:^(int32_t outcome){
        result = outcome;
    }];
    SYNC_WAIT;
    XCTAssertEqual(result, 42, @"The platform callback has returned an unexpected value");
}

- (void)testNoParametersNoReturnAsyncCallback {
    NoParametersNoReturnCallbackImpl* callback = [[NoParametersNoReturnCallbackImpl alloc] init];
    __block BOOL completionCalled = NO;
    [self.asynchronous noParametersNoReturnCallback:callback completion:^(){
        completionCalled = YES;
    }];
    SYNC_WAIT;
    XCTAssertEqual(completionCalled, YES, @"The completion handler was not called");
}

@end

@implementation MultiplyCallbackImpl
- (void)invoke:(int32_t)a b:(int32_t)b completion:(void (^)(int32_t))completion {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        completion(a * b);
    });
}
@end

@implementation NoParametersNoReturnCallbackImpl
- (void)invoke:(void (^)(void))completion {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        completion();
    });
}

@end
