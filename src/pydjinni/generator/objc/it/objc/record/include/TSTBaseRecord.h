#import <Foundation/Foundation.h>
#import "TSTBaseRecordBase.h"

NS_SWIFT_NAME(BaseRecord)
@interface TSTBaseRecord : TSTBaseRecordBase
- (nonnull instancetype)initWithValue:(int32_t)value;
+ (nonnull instancetype)baseRecordWithValue:(int32_t)value;
- (nonnull instancetype)init;
+ (nonnull instancetype)baseRecord;
@end
