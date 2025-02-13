import XCTest
import ErrorTestSwift

final class FunctionTests: XCTestCase {
    func testRaisingError() {
        XCTAssertThrowsError(try Helper.throwingError()) { error in
            XCTAssertEqual(error as! FooError, FooError(FooError.somethingWrong, userInfo: [
                NSLocalizedDescriptionKey: "some error"
            ]))
        }
    }
    
    func testRaisingErrorWithParameter() {
        XCTAssertThrowsError(try Helper.throwingWithParameters()) { error in
            XCTAssertEqual(error as! FooError, FooError(FooError.somethingWithParameters, userInfo: [
                NSLocalizedDescriptionKey: "some error message",
                FooErrorSomethingWithParametersParameter: 42
            ]))
        }
    }
    
    func testRaisingErrorAsync() async {
        await AssertThrowsAsyncError( try await Helper.throwingAsync(), expectedError: FooError(FooError.somethingWrong, userInfo: [
            NSLocalizedDescriptionKey: "something wrong in coroutine"
        ]))
    }
    
    func testRaisingCallbackError() {
        class ThrowingCallbackImpl : ThrowingCallback {
            var invoked = false
            func throwingError() throws {
                invoked = true
                throw FooError(FooError.somethingWrong, userInfo: [
                    NSLocalizedDescriptionKey: "some callback error"
                ])
            }
        }
        let callback = ThrowingCallbackImpl()
        XCTAssertThrowsError(try Helper.throwingCallbackError(callback: callback)) { error in
            XCTAssertEqual(error as! FooError, FooError(FooError.somethingWrong, userInfo: [
                NSLocalizedDescriptionKey: "some callback error"
            ]))
        }
        XCTAssertTrue(callback.invoked)
    }
    
    func testRaisingAsyncCallbackError() async {
        class AsyncThrowingCallbackImplementation : AsyncThrowingCallback {
            var invoked = false
            func throwingError() async throws {
                invoked = true
                throw FooError(FooError.somethingWrong, userInfo: [
                    NSLocalizedDescriptionKey: "some async callback error"
                ])
            }
        }
        let callback = AsyncThrowingCallbackImplementation()
        await AssertThrowsAsyncError(try await Helper.throwingAsyncCallbackError(callback: callback), expectedError: FooError(FooError.somethingWrong, userInfo: [
            NSLocalizedDescriptionKey: "some async callback error"
        ]))
        XCTAssertTrue(callback.invoked)
    }
    
    func AssertThrowsAsyncError<T, E: Error & Equatable>(
        _ expression: @autoclosure () async throws -> T,
        expectedError: E,
        _ message: @autoclosure () -> String = "Expected error to be thrown",
        file: StaticString = #filePath,
        line: UInt = #line
    ) async {
        do {
            _ = try await expression()
            XCTFail("Should have thrown an error", file: file, line: line)
        } catch let error as E {
            XCTAssertEqual(error, expectedError, message(), file: file, line: line)
        } catch {
            XCTFail("Unexpected error: \(error)", file: file, line: line)
        }
    }
}
