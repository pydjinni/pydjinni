#import <XCTest/XCTest.h>
#import "Helper.h"

@interface EnumTests : XCTestCase
@end

@implementation EnumTests

- (void)testEnum {
    XCTAssertEqual([Helper getEnum:ExampleEnumA], ExampleEnumA, @"Returned Enum does not match input");
}

@end
