// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#import <Foundation/Foundation.h>
#import "pydjinni/deprecated.hpp"
NS_SWIFT_NAME(DeprecatedFieldRecord)
@interface SFTDeprecatedFieldRecord : NSObject
- (nonnull instancetype)initWithOld:(int32_t)old older:(nullable NSNumber *)older;
+ (nonnull instancetype)deprecatedFieldRecordWithOld:(int32_t)old older:(nullable NSNumber *)older;
@property (nonatomic, readonly) int32_t old
DEPRECATED_MSG_ATTRIBUTE("the field is old");
/// foo
@property (nonatomic, readonly, nullable) NSNumber * older
DEPRECATED_MSG_ATTRIBUTE("this is optional and old");
@end
