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
#import "Asynchronous.h"

// Runs the NSRunLoop for a short time to allow the async methods to dispatch a callback.
#define SYNC_WAIT [[NSRunLoop mainRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.05]]

@interface PlatformCallback : NSObject <Callback>
@end

@interface AsyncTests : XCTestCase

@property (nonatomic, strong) Asynchronous * asynchronous;

@end

@implementation AsyncTests

- (void)setUp {
    [Asynchronous getInstance: ^(Asynchronous * result){
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

- (void)testPlatformCallback {
    PlatformCallback* callback = [[PlatformCallback alloc] init];
    __block int32_t result;
    [self.asynchronous callback:callback completion:^(int32_t outcome){
        result = outcome;
    }];
    SYNC_WAIT;
    XCTAssertEqual(result, 42, @"The platform callback has returned an unexpected value");
}

@end

@implementation PlatformCallback
- (void)multiply:(int32_t)a b:(int32_t)b completion:(void (^)(int32_t))completion {
    completion(a * b);
}

@end
