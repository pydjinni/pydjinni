// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
#import <Foundation/Foundation.h>
#import "TSTFunctionCppCppcliJavaObjcYamlFooBool.h"
#import "TSTFunctionCppCppcliJavaObjcYamlStringBool.h"
#import "TSTFunctionCppCppcliJavaObjcYamlVoidThrows.h"
#import "TSTFunctionCppCppcliJavaObjcYamlVoidThrowsBar.h"
#import "TSTNamedFunction.h"
#import "TSTThrowingFunction.h"
@interface TSTHelper : NSObject
+ (void)namedFunction:(BOOL (^ _Nonnull)(NSString * _Nonnull))callback;
+ (void)anonymousFunction:(BOOL (^ _Nonnull)(NSString * _Nonnull))callback;
+ (BOOL (^ _Nonnull)(NSString * _Nonnull))cppNamedFunction;
+ (BOOL (^ _Nonnull)(NSString * _Nonnull))cppAnonymousFunction;
+ (void (^ _Nonnull)(NSError* _Nullable * _Nonnull))cppFunctionThrowingException;
+ (void (^ _Nonnull)(NSError* _Nullable * _Nonnull))cppFunctionThrowingBarError;
+ (void)anonymousFunctionPassingRecord:(BOOL (^ _Nonnull)(TSTFoo * _Nonnull))callback;
+ (void)functionParameterThrowing:(void (^ _Nonnull)(NSError* _Nullable * _Nonnull))callback error:(NSError* _Nullable * _Nonnull)error;
+ (BOOL (^ _Nullable)(NSString * _Nonnull))optionalFunctionPassingNull:(BOOL (^ _Nullable)(NSString * _Nonnull))param;
+ (BOOL (^ _Nullable)(NSString * _Nonnull))optionalFunctionPassingFunction:(BOOL (^ _Nullable)(NSString * _Nonnull))param;
@end
