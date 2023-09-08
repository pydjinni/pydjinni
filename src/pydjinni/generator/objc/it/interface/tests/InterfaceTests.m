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
    readwriteValueUpdates = 0;
    readonlyValueUpdates = 0;
    readwriteNewValue = -1;
    readwriteOldValue = -1;
    readonlyNewValue = -1;
    readonlyOldValue = -1;
}

- (void)testCalculator {
    int8_t result = [self.calculator add:40 b:2];
    XCTAssertEqual(result, 42, @"The calculator has returned an unexpected value");
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

static void *ReadWriteValueContext = &ReadWriteValueContext;
static void *ReadonlyValueContext = &ReadonlyValueContext;
int32_t readwriteValueUpdates; // number of times the property 'readwriteValue' was updated
int32_t readwriteNewValue;
int32_t readwriteOldValue;
int32_t readonlyValueUpdates; // number of times the property 'readonlyValue' was updated
int32_t readonlyNewValue;
int32_t readonlyOldValue;

- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary *)change
                       context:(void *)context {

    if (context == ReadWriteValueContext) {
        readwriteValueUpdates++;
        [[change valueForKey:NSKeyValueChangeOldKey] getValue:&readwriteOldValue];
        [[change valueForKey:NSKeyValueChangeNewKey] getValue:&readwriteNewValue];

    } else if (context == ReadonlyValueContext) {
        readonlyValueUpdates++;
        [[change valueForKey:NSKeyValueChangeOldKey] getValue:&readonlyOldValue];
        [[change valueForKey:NSKeyValueChangeNewKey] getValue:&readonlyNewValue];
    }
}

- (void)testReadonlyProperty {
    int32_t value = self.calculator.readonlyValue;
    XCTAssertEqual(value, 0);
}

- (void)testReadwriteProperty {
    [self.calculator addObserver:self
              forKeyPath:@"readwriteValue"
                 options:(NSKeyValueObservingOptionNew |
                          NSKeyValueObservingOptionOld)
                 context:ReadWriteValueContext];
    self.calculator.readwriteValue = 5;
    int32_t newValue = self.calculator.readwriteValue;
    XCTAssertEqual(newValue, 5);
    XCTAssertEqual(readwriteOldValue, 0);
    XCTAssertEqual(readwriteNewValue, 5);
    XCTAssertEqual(readwriteValueUpdates, 1);
}

- (void)testReadonlyPropertyUpdate {
    [self.calculator addObserver:self
                      forKeyPath:@"readonlyValue"
                         options:(NSKeyValueObservingOptionNew |
                                  NSKeyValueObservingOptionOld)
                         context:ReadonlyValueContext];
    [self.calculator updateReadonlyProperty: 42];
    int32_t newValue = self.calculator.readonlyValue;
    XCTAssertEqual(newValue, 42);
    XCTAssertEqual(readonlyOldValue, 0);
    XCTAssertEqual(readonlyNewValue, 42);
    XCTAssertEqual(readonlyValueUpdates, 1);
}

@end

@implementation PlatformImplementation
- (int8_t)getValue {
    return 5;
}
@synthesize readonlyValue;

@synthesize readwriteValue;

@end
