// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.pydjinni'
#import <Foundation/Foundation.h>
#import "TSTCalculator.h"
#import "TSTNoParametersNoReturnCallback.h"
#import "TSTPlatformInterface.h"
#import "TSTThrowingCallback.h"
NS_SWIFT_NAME(Calculator)
@interface TSTCalculator : NSObject
+ (nullable TSTCalculator *)getInstance
  NS_SWIFT_NAME(getInstance());
/// adds up two values
/// 
/// - Parameter a: the first value
/// - Parameter b: the second value
/// - Returns: the sum of both values
- (int8_t)add:(int8_t)a b:(int8_t)b
  NS_SWIFT_NAME(add(a:b:));
- (int8_t)getPlatformValue:(nullable id<TSTPlatformInterface>)platform
  NS_SWIFT_NAME(getPlatformValue(platform:));
- (void)noParametersNoReturn
  NS_SWIFT_NAME(noParametersNoReturn());
- (void)throwingException:(NSError* _Nullable * _Nonnull)error
  __attribute__((swift_error(nonnull_error)))
  NS_SWIFT_NAME(throwingException(error:));
- (void)noParametersNoReturnCallback:(nullable id<TSTNoParametersNoReturnCallback>)callback
  NS_SWIFT_NAME(noParametersNoReturnCallback(callback:));
- (void)throwingCallback:(nullable id<TSTThrowingCallback>)callback error:(NSError* _Nullable * _Nonnull)error
  __attribute__((swift_error(nonnull_error)))
  NS_SWIFT_NAME(throwingCallback(callback:error:));
@end
