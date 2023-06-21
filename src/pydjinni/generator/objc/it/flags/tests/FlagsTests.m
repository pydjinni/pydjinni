#import <XCTest/XCTest.h>
#import "Helper.h"

@interface FlagsTests : XCTestCase
@end

@implementation FlagsTests

- (void)testFlags {
    XCTAssertEqual([Helper getFlag:ExampleFlagsA], ExampleFlagsA, @"Returned Flag does not match input");
}

- (void)testAllFlags {
    XCTAssertEqual([Helper getAllFlag:ExampleFlagsAll], ExampleFlagsAll, @"Returned Flag does not match input");
}

- (void)testNoneFlags {
    XCTAssertEqual([Helper getNoneFlag:ExampleFlagsNone], ExampleFlagsNone, @"Returned Flag does not match input");
}


@end
