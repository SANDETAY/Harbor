import UIKit
import Capacitor

/// Capacitor 6 only auto-registers plugins listed in packageClassList (npm packages).
/// Local app plugins like HarborWidgets must be registered here so the web layer can push snapshots.
///
/// Storyboard must use customModule matching PRODUCT_MODULE_NAME (`Harbor`), not `App`.
@objc(HarborBridgeViewController)
class HarborBridgeViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        super.capacitorDidLoad()
        bridge?.registerPluginType(HarborWidgetsPlugin.self)
        bridge?.registerPluginType(HarborSpeechPlugin.self)
    }
}
