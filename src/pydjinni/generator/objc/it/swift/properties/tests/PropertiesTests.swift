import XCTest
import PropertiesTestSwift

final class PropertiesTests: XCTestCase {
    let properties = CppProperties.getInstance()

    func testPropertySetter() {
        properties.readwriteProperty = 42
        XCTAssertEqual(properties.readwriteProperty, 42)
    }

    func testPropertyKVO() {
        var observedReadwritePropertyValue: Int64 = 0
        withExtendedLifetime(observe(
            \.properties.readwriteProperty,
            options: [.old, .new]
        ) { object, change in
            observedReadwritePropertyValue = change.newValue ?? 0
        }) {
            properties.readwriteProperty = 42
        }
        XCTAssertEqual(observedReadwritePropertyValue, 42)
    }

    func testReadonlyPropertyChangedThroughSideEffect() {
        var observedReadonlyPropertyValue: String = "uncalled";
        withExtendedLifetime(observe(
            \.properties.readonlyProperty,
            options: [.old, .new]
        ) { object, change in
            observedReadonlyPropertyValue = change.newValue ?? "uncalled";
        }) {
            properties.changeReadonlyProperty()
        }
        XCTAssertEqual(properties.readonlyProperty, "changed")
        XCTAssertEqual(observedReadonlyPropertyValue, "changed")
    }

    func testOptionalPropertyNonnullValue() {
        var observedOptionalPropertyValue: Int64? = 0;
        withExtendedLifetime(observe(
            \.properties.optionalProperty,
            options: [.old, .new]
        ) { object, change in
            observedOptionalPropertyValue = change.newValue??.int64Value;
        }) {
            properties.optionalProperty = 42
        }
        XCTAssertEqual(properties.optionalProperty, 42)
        XCTAssertEqual(observedOptionalPropertyValue, 42)
    }

    func testOptionalPropertyNullValue() {
        var observedOptionalPropertyValue: Int64? = 0
        withExtendedLifetime(observe(
            \.properties.optionalProperty,
            options: [.old, .new]
        ) { object, change in
            observedOptionalPropertyValue = change.newValue??.int64Value;
        }) {
            properties.optionalProperty = nil;
        }
        XCTAssertNil(properties.optionalProperty)
        XCTAssertNil(observedOptionalPropertyValue)
    }
}
