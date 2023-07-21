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
