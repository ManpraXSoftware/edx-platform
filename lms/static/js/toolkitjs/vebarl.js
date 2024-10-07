if (typeof window["AtKit"] == "undefined") {
	// Load AtKit
	d = document; jf = d.createElement('script'); jf.src = document.getElementById("external_js").getAttribute('lms_base_url') + 'static/js/toolkitjs/atkit.js'; jf.type = 'text/javascript'; jf.id = 'AtKitLib'; d.getElementsByTagName('head')[0].appendChild(jf);
	window.AtKitLoaded = function () {
		var eventAction = null;

		this.subscribe = function (fn) {
			eventAction = fn;
		};

		this.fire = function (sender, eventArgs) {
			if (eventAction != null) {
				eventAction(sender, eventArgs);
			}
		};
	}

	window["AtKitLoaded"] = new AtKitLoaded();
	window["AtKitLoaded"].subscribe(function () { __start(); });
} else {
	__start();
}

function __start() {

	// Start toolbar code
	(function (window, AtKit) {

		$ = AtKit.lib();

		var settings = {
			"version": "1.0"
		};

		settings.baseURL = ("https:" == document.location.protocol ? "https://ssl.atbar.org/c/ATBar/" : "http://c.atbar.org/ATBar/");

		var plugins = ["tooltip"];

		var onLoad = function () {

			// Set our logo

			AtKit.setLanguage("en");

			var about = "Version " + settings.version;
			about += "My Toolbar";

			AtKit.setAbout(about);



			// Add all the plugins to the toolbar
			$.each(plugins, function (i, v) {
				AtKit.addPlugin(v);
			});


			AtKit.addPlugin("resize");
			AtKit.addPlugin("fonts1");
			AtKit.addPlugin("css1");
			AtKit.addPlugin("link");
			AtKit.addPlugin("back");
			// AtKit.addPlugin("insipio-tts");
			AtKit.addPlugin("fonts");



			AtKit.addResetFn("reset-saved", function () {
				localStorage.bColour = undefined
				localStorage.lHeight = undefined
				localStorage.linkColour = undefined
				localStorage.textColour = undefined
				localStorage.fSize = undefined
				localStorage.fFace = undefined
			});


			// Run
			AtKit.render();
		};


		AtKit.importPlugins(plugins, onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/resize.js', onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/fc.js', onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/lc.js', onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/fontface.js', onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/lineheight.js', onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/bc.js', onLoad);
		AtKit.addScript(document.getElementById("external_js").getAttribute("lms_base_url") + 'static/js/toolkitjs/tts.js', onLoad);



	}(window, AtKit));

}