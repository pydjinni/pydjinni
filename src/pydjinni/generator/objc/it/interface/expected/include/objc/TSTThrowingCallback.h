// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.pydjinni'
#import <Foundation/Foundation.h>
NS_SWIFT_NAME(ThrowingCallback)
@protocol TSTThrowingCallback <NSObject>
- (void)invoke:(NSError* _Nullable * _Nonnull)error
  __attribute__((swift_error(nonnull_error)))
  NS_SWIFT_NAME(invoke(error:));
@end
