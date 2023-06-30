#import <XCTest/XCTest.h>
#import "Helper.h"

@interface OptionalTypesTests : XCTestCase

@property (nonatomic, strong) OptionalTypes * record;

@end

@implementation OptionalTypesTests

- (void)setUp {
    self.record = [OptionalTypes optionalTypesWithIntOptional: @42 stringOptional: @"optional"];
}

- (void)testOptionalTypes {
    OptionalTypes* returned_record = [Helper getOptionalTypes:self.record];

    XCTAssertEqualObjects(returned_record.intOptional, @42);
    XCTAssertEqualObjects(returned_record.stringOptional, @"optional");
}

- (void)testDescription {
    XCTAssertEqualObjects([self.record description], @"<OptionalTypes intOptional:42 stringOptional:optional>");
}

@end
