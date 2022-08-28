finergy.provide('finergy.barcode');

finergy.barcode.scan_barcode = function() {
	return new Promise((resolve, reject) => {
		if (
			window.cordova &&
			window.cordova.plugins &&
			window.cordova.plugins.barcodeScanner
		) {
			window.cordova.plugins.barcodeScanner.scan(result => {
				if (!result.cancelled) {
					resolve(result.text);
				}
			}, reject);
		} else {
			finergy.require('/assets/js/barcode_scanner.min.js', () => {
				finergy.barcode.get_barcode().then(barcode => {
					resolve(barcode);
				});
			});
		}
	});
};
