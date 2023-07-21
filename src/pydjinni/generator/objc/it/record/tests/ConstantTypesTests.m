#import <XCTest/XCTest.h>
#import "ConstantTypes.h"

@interface ConstantTypesTests : XCTestCase
@end

@implementation ConstantTypesTests

- (void)testConstantTypes {
    XCTAssertEqual(ConstantTypesBooleanc, YES);
    XCTAssertEqual(ConstantTypesBytec, 8);
    XCTAssertEqual(ConstantTypesShortc, 16);
    XCTAssertEqual(ConstantTypesIntc, 32);
    XCTAssertEqual(ConstantTypesLongc, 64);
    XCTAssertGreaterThan(ConstantTypesFloatc, 32);
    XCTAssertLessThan(ConstantTypesFloatc, 33);
    XCTAssertGreaterThan(ConstantTypesDoublec, 64);
    XCTAssertLessThan(ConstantTypesDoublec, 65);
    XCTAssertEqualObjects(ConstantTypesStringc, @"foo");
}

@end
