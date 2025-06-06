// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#import <Foundation/Foundation.h>
#import "SFTBaseRecord.h"
#import "SFTBinaryTypes.h"
#import "SFTCollectionTypes.h"
#import "SFTOptionalTypes.h"
#import "SFTParentType.h"
#import "SFTPrimitiveTypes.h"
NS_SWIFT_NAME(Helper)
@interface SFTHelper : NSObject
+ (nonnull SFTPrimitiveTypes *)getPrimitiveTypes:(nonnull SFTPrimitiveTypes *)recordType
  NS_SWIFT_NAME(getPrimitiveTypes(recordType:));
+ (nonnull SFTCollectionTypes *)getCollectionTypes:(nonnull SFTCollectionTypes *)recordType
  NS_SWIFT_NAME(getCollectionTypes(recordType:));
+ (nonnull SFTOptionalTypes *)getOptionalTypes:(nonnull SFTOptionalTypes *)recordType
  NS_SWIFT_NAME(getOptionalTypes(recordType:));
+ (nonnull SFTBinaryTypes *)getBinaryTypes:(nonnull SFTBinaryTypes *)recordType
  NS_SWIFT_NAME(getBinaryTypes(recordType:));
+ (nonnull SFTBaseRecord *)getCppBaseRecord
  NS_SWIFT_NAME(getCppBaseRecord());
+ (nonnull SFTBaseRecord *)getHostBaseRecord:(nonnull SFTBaseRecord *)recordType
  NS_SWIFT_NAME(getHostBaseRecord(recordType:));
+ (nonnull SFTParentType *)getNestedType:(nonnull SFTParentType *)parent
  NS_SWIFT_NAME(getNestedType(parent:));
@end
