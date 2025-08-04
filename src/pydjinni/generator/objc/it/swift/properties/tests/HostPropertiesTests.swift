import XCTest
import PropertiesTestSwift

final class HostPropertiesTests: XCTestCase {
    class HostPropertiesImpl: NSObject, HostProperties {
        @objc dynamic var readwriteProperty: Int64 = 0
        @objc dynamic var readonlyProperty: String = "initial"
        @objc dynamic var optionalProperty: NSNumber? = 0

        func changeReadonlyProperty() {
            readonlyProperty = "changed"
        }
    }
    var hostProperties: HostProperties!
    var helper: HostPropertyHelper!
    
    override func setUp() {
        super.setUp()
        hostProperties = HostPropertiesImpl()
        helper = HostPropertyHelper.setup(properties: hostProperties)
    }

    func testChangingReadwriteHostProperty() {
        hostProperties.readwriteProperty = 42
        let result = helper.readwritePropertyData()
        XCTAssertEqual(result.changeCounter, 1)
        XCTAssertEqual(result.callbackValue, 42)
        XCTAssertEqual(result.readValue, 42)
    }

    func testChangingReadonlyHostProperty() {
        hostProperties.changeReadonlyProperty()
        let result = helper.readonlyPropertyData()
        XCTAssertEqual(result.changeCounter, 1)
        XCTAssertEqual(result.callbackValue, "changed")
        XCTAssertEqual(result.readValue, "changed")
    }

    func testChangingHostPropertyFromHelper() {
        var observedValue: Int64 = 0;
        withExtendedLifetime(observe(
            \.hostProperties.readwriteProperty,
            options: [.new]
        ) { object, change in
            observedValue = change.newValue ?? 0;
        }) {
            helper.modifyHostReadwriteProperty()
        }
        let result = helper.readwritePropertyData()
        XCTAssertEqual(hostProperties.readwriteProperty, 2);
        XCTAssertEqual(observedValue, 2);
        XCTAssertEqual(result.changeCounter, 1)
        XCTAssertEqual(result.callbackValue, 2)
        XCTAssertEqual(result.readValue, 2)
    }

    func testChangingOptionalHostPropertyNonnull() {
        hostProperties.optionalProperty = 42
        let result = helper.optionalPropertyData()
        XCTAssertEqual(result.changeCounter, 1)
        XCTAssertEqual(result.callbackValue, 42)
        XCTAssertEqual(result.readValue, 42)
    }

    func testChangingOptionalHostPropertyNil() {
        hostProperties.optionalProperty = nil
        let result = helper.optionalPropertyData()
        XCTAssertEqual(result.changeCounter, 1)
        XCTAssertNil(result.callbackValue)
        XCTAssertNil(result.readValue)
    }
}
