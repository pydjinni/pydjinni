// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.djinni'
#import "SFTBaseRecord.h"

@implementation SFTBaseRecord

- (nonnull instancetype)initWithValue:(int32_t)value {
    return [super initWithValue: value];
}

+ (nonnull instancetype)baseRecordWithValue:(int32_t)value {
    return [(SFTBaseRecord*)[self alloc] initWithValue:value];
}

- (nonnull instancetype)init {
    return [self initWithValue: 42];
}

+ (nonnull instancetype)baseRecord {
    return [(SFTBaseRecord*)[self alloc] init];
}

@end
