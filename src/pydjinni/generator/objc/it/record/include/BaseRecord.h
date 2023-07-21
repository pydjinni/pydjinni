#import <Foundation/Foundation.h>
#import "BaseRecordBase.h"

NS_SWIFT_NAME(BaseRecord)
@interface BaseRecord : BaseRecordBase
- (nonnull instancetype)initWithValue:(int32_t)value;
+ (nonnull instancetype)baseRecordWithValue:(int32_t)value;
- (nonnull instancetype)init;
+ (nonnull instancetype)baseRecord;
@end
