#import <XCTest/XCTest.h>
#import "Calculator.h"

@interface PlatformImplementation : NSObject <PlatformInterface>
@end

@interface InterfaceTests : XCTestCase

@property (nonatomic, strong) Calculator * calculator;

@end

@implementation InterfaceTests

- (void)setUp {
    self.calculator = [Calculator getInstance];
}

- (void)testCalculator {
    int8_t result = [self.calculator add:40 b:2];
    XCTAssertEqual(result, 42, @"The calculator has returned an unexpected value");
}

- (void)testConstant {
    XCTAssertEqual(CalculatorA, 5, @"The constant does not have the expected value");
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

@end

@implementation PlatformImplementation
- (int8_t)getValue {
    return 5;
}
@end
