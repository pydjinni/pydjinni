#import <Foundation/Foundation.h>
#import "SFTBaseRecordBase.h"

NS_SWIFT_NAME(BaseRecord)
@interface SFTBaseRecord : SFTBaseRecordBase
- (nonnull instancetype)initWithValue:(int32_t)value;
+ (nonnull instancetype)baseRecordWithValue:(int32_t)value;
- (nonnull instancetype)init;
+ (nonnull instancetype)baseRecord;
@end
