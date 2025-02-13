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
#import "TSTHelper.h"
#import "TSTFooError.h"

// Runs the NSRunLoop for a short time to allow the async methods to dispatch a callback.
#define SYNC_WAIT [[NSRunLoop mainRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.05]]

@interface ThrowingCallbackImplementation : NSObject <TSTThrowingCallback>
@property BOOL callbackInvoked;
@end

@interface AsyncThrowingCallbackImplementation : NSObject <TSTAsyncThrowingCallback>
@property BOOL callbackInvoked;
@end

@interface ErrorTests : XCTestCase
@end

@implementation ErrorTests


- (void)testRaisingError {
    NSError * error;
    [TSTHelper throwingError:&error];
    XCTAssertNotNil(error);
    XCTAssertEqual(error.domain, TSTFooErrorDomain);
    XCTAssertEqual(error.code, TSTFooErrorSomethingWrong);
    XCTAssertEqualObjects(error.localizedDescription, @"some error");
}

- (void)testRaisingErrorWithParameter {
    NSError * error;
    [TSTHelper throwingWithParameters:&error];
    XCTAssertNotNil(error);
    XCTAssertEqual(error.domain, TSTFooErrorDomain);
    XCTAssertEqual(error.code, TSTFooErrorSomethingWithParameters);
    XCTAssertEqualObjects(error.localizedDescription, @"some error message");
    XCTAssertEqualObjects([error.userInfo valueForKey: TSTFooErrorSomethingWithParametersParameter], @42);
}

- (void)testRaisingErrorAsync {
    __block NSError* error_result;

    [TSTHelper throwingAsync:^(NSError * error){
        error_result = error;
    }];
    SYNC_WAIT;
    XCTAssertNotNil(error_result);
    XCTAssertEqual(error_result.domain, TSTFooErrorDomain);
    XCTAssertEqual(error_result.code, TSTFooErrorSomethingWrong);
    XCTAssertEqualObjects(error_result.localizedDescription, @"something wrong in coroutine");
}

- (void)testRaisingCallbackError {
    NSError* error;
    ThrowingCallbackImplementation* callback = [[ThrowingCallbackImplementation alloc] init];
    [TSTHelper throwingCallbackError:callback error:&error];
    XCTAssertTrue(callback.callbackInvoked, @"Callback was not invoked");
    XCTAssertNotNil(error);
    XCTAssertEqual(error.domain, TSTFooErrorDomain);
    XCTAssertEqual(error.code, TSTFooErrorSomethingWrong);
    XCTAssertEqualObjects(error.localizedDescription, @"some callback error");
}

- (void)testRaisingAsyncCallbackError {
    __block NSError* error_result;
    AsyncThrowingCallbackImplementation* callback = [[AsyncThrowingCallbackImplementation alloc] init];
    [TSTHelper throwingAsyncCallbackError:callback completion:^(NSError * error){
        error_result = error;
    }];
    SYNC_WAIT;
    XCTAssertNotNil(error_result);
    XCTAssertEqual(error_result.domain, TSTFooErrorDomain);
    XCTAssertEqual(error_result.code, TSTFooErrorSomethingWrong);
    XCTAssertEqualObjects(error_result.localizedDescription, @"some async callback error");
}


@end

@implementation ThrowingCallbackImplementation

-(id)init {
    if (self = [super init])  {
        self.callbackInvoked = NO;
    }
    return self;
}

- (void)throwingError:(NSError * _Nullable * _Nonnull)error {
    self.callbackInvoked = YES;
    NSString *desc = NSLocalizedString(@"some callback error", @"");
    NSDictionary *userInfo = @{ NSLocalizedDescriptionKey : desc };
    *error = [NSError errorWithDomain:TSTFooErrorDomain
                                code:TSTFooErrorSomethingWrong
                            userInfo:userInfo];
}

@end

@implementation AsyncThrowingCallbackImplementation

-(id)init {
    if (self = [super init])  {
        self.callbackInvoked = NO;
    }
    return self;
}

- (void)throwingError:(nonnull void (^)(NSError * _Nullable))completion {
    self.callbackInvoked = YES;
    NSString *desc = NSLocalizedString(@"some async callback error", @"");
    NSDictionary *userInfo = @{ NSLocalizedDescriptionKey : desc };
    completion([NSError errorWithDomain:TSTFooErrorDomain
                                   code:TSTFooErrorSomethingWrong
                               userInfo:userInfo]);
}

@end
