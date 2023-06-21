#import <XCTest/XCTest.h>
#import "Calculator.h"

@interface PlatformImplementation : NSObject <PlatformInterface>
@end

@interface InterfaceTests : XCTestCase
@end

@implementation InterfaceTests

- (void)testCalculator {
    Calculator* calculator = [Calculator getInstance];
    int8_t result = [calculator add:40 b:2];
    XCTAssertEqual(result, 42, @"The calculator has returned an unexpected value");
}

- (void)testConstant {
    XCTAssertEqual(CalculatorA, 5, @"The constant does not have the expected value");
}


- (void)testPlatformImplementation {
    Calculator* calculator = [Calculator getInstance];
    PlatformImplementation* implementation = [[PlatformImplementation alloc] init];
    int8_t result = [calculator getPlatformValue:implementation];
    XCTAssertEqual(result, 5, @"The result from the Objective-C implementation was not as expected");
}

@end

@implementation PlatformImplementation
- (int8_t)getValue {
    return 5;
}
@end