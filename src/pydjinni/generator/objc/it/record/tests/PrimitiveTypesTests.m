#import <XCTest/XCTest.h>
#import "Helper.h"

@interface PrimitiveTypesTests : XCTestCase

@property (nonatomic, strong) PrimitiveTypes * record;

@end

@implementation PrimitiveTypesTests

- (void)setUp {
    self.record = [PrimitiveTypes primitiveTypesWithBooleanT:YES
                                                       byteT:8
                                                      shortT:16
                                                        intT:32
                                                       longT:64
                                                      floatT:32.32f
                                                     doubleT:64.64
                                                     stringT:@"test string"];
}

- (void)testPrimitiveTypes {
    PrimitiveTypes* returned_record = [Helper getPrimitiveTypes:self.record];

    XCTAssertEqual(returned_record.booleanT, YES);
    XCTAssertEqual(returned_record.byteT, 8);
    XCTAssertEqual(returned_record.shortT, 16);
    XCTAssertEqual(returned_record.intT, 32);
    XCTAssertEqual(returned_record.longT, 64);
    XCTAssertGreaterThan(returned_record.floatT, 32);
    XCTAssertLessThan(returned_record.floatT, 33);
    XCTAssertGreaterThan(returned_record.doubleT, 64);
    XCTAssertLessThan(returned_record.doubleT, 65);
    XCTAssertEqualObjects(returned_record.stringT, @"test string");
}

- (void)testDescription {
    XCTAssertEqualObjects([self.record description], @"<PrimitiveTypes booleanT:YES byteT:8 shortT:16 intT:32 longT:64 floatT:32.32 doubleT:64.64 stringT:test string>");
}

@end
