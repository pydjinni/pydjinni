import XCTest
import FunctionTestSwift

final class FunctionTests: XCTestCase {
    func testNamedFunction() {
        Helper.namedFunction(callback: { input in
            return input == "foo"
        })
    }
    
    func testAnonymousFunction() {
        Helper.anonymousFunction(callback: { input in
            return input == "foo"
        })
    }
    
    func testCppNamedFunction() {
        let block = Helper.cppNamedFunction()
        let result = block("foo")
        XCTAssertTrue(result)
    }
    
    func testCppAnonymousFunction() {
        let block = Helper.cppAnonymousFunction()
        let result = block("foo")
        XCTAssertTrue(result)
    }
    
    func testCppFunctionThrowingException() {
        let block = Helper.cppFunctionThrowingException()
        var error: NSError?
        block(&error)
        XCTAssertNotNil(error)
        XCTAssertEqual(error?.localizedDescription, "shit hit the fan")
    }
    
    func testCppFunctionThrowingBarError() {
        let block = Helper.cppFunctionThrowingBarError()
        var error: NSError?
        block(&error)
        XCTAssertNotNil(error)
        XCTAssertEqual(error?.domain, Bar.errorDomain)
        XCTAssertEqual(error?.code, Bar.badStuff.rawValue)
        XCTAssertEqual(error?.localizedDescription, "this lambda has thrown an exception")
    }
    
    func testAnonymousFunctionPassingRecord() {
        Helper.anonymousFunctionPassingRecord(callback: { foo in
            return foo.a == 32
        })
    }
    
    func testFunctionParameterThrowing() {
        XCTAssertThrowsError(try Helper.functionParameterThrowing(callback: {error in
            error?.pointee = NSError(domain: NSCocoaErrorDomain, code: NSFileNoSuchFileError, userInfo: [
                NSLocalizedDescriptionKey: "unexpected error from host",
                NSFilePathErrorKey: "some.file"
            ])
        })) { error in
            XCTAssertEqual(error as NSError, NSError(domain: NSCocoaErrorDomain, code: NSFileNoSuchFileError, userInfo: [
                NSLocalizedDescriptionKey: "unexpected error from host",
                NSFilePathErrorKey: "some.file"
            ]))
        }
    }
}
