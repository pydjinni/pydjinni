#import <XCTest/XCTest.h>
#import "Helper.h"

@interface BinaryTypesTests : XCTestCase

@property (nonatomic, strong) BinaryTypes * record;

@end

@implementation BinaryTypesTests

- (void)setUp {
    const unsigned char byteArray[] = {0x8F};
    self.record = [BinaryTypes binaryTypesWithBinaryT: [NSData dataWithBytes:byteArray length:sizeof(byteArray)]
                                          binaryOptional: [NSData dataWithBytes:byteArray length:sizeof(byteArray)]];
}

- (void)testBinaryTypes {
    BinaryTypes* returned_record = [Helper getBinaryTypes:self.record];

    XCTAssertEqual(returned_record.binaryT.length, 1);
    XCTAssertEqual(returned_record.binaryOptional.length, 1);
}

@end
