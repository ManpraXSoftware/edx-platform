(function() {
    var e = function() {
        $lib = AtKit.lib();
        AtKit.addLocalisationMap("en", {
            fonts_dialogTitle: "Page Font Settings",
            fonts_fontFace: "Font Face",
            //fonts_lineSpacing: "Line Spacing",
            fonts_apply: "Apply"
        });
        AtKit.addLocalisationMap("ar", {
            fonts_dialogTitle: "&#1575;&#1604;&#1578;&#1581;&#1603;&#1605; &#1601;&#1610; &#1606;&#1608;&#1593; &#1575;&#1604;&#1582;&#1591;",
            fonts_fontFace: "&#1606;&#1608;&#1593; &#1575;&#1604;&#1582;&#1591;",
            fonts_lineSpacing: "&#1575;&#1604;&#1605;&#1587;&#1575;&#1601;&#1575;&#1578; &#1576;&#1610;&#1606; &#1575;&#1604;&#1571;&#1587;&#1591;&#1585;",
            fonts_apply: "&#1578;&#1591;&#1576;&#1610;&#1602;"
        });
        var d = {
            main: "<h1>" + AtKit.localisation("fonts_dialogTitle") + '</h1><label for="sbfontface">' + AtKit.localisation("fonts_fontFace") + ':</label> <select id="sbfontface"><option value="sitespecific">--Site Specific--</option><option value="arial">Arial</option><option value="courier">Courier</option><option value="cursive">Cursive</option><option value="fantasy">Fantasy</option><option value="georgia">Georgia</option><option value="helvetica">Helvetica</option><option value="impact">Impact</option><option value="monaco">Monaco</option><option value="monospace">Monospace</option><option value="sans-serif">Sans-Serif</option><option value="tahoma">Tahoma</option><option value="times new roman">Times New Roman</option><option value="trebuchet ms">Trebuchet MS</option><option value="verdant">Verdana</option></select><br /><br /><button id="ATApplyFont">' + AtKit.localisation("fonts_apply") + "</a></div>"
        };
        AtKit.addFn("changeFont", function(a) {
            var c = AtKit.getHtmlTags();
            if ("--Site Specific--" != a.fontFace) {
                for (var b = 0; b < c.length; b++){
                   $lib(c[b]).css("font-family", a.fontFace);
                }
                for (b = 0; b < c.length; b++) $lib(c[b]).css("line-height", a.lineHeight + "%");
                $lib("#sbar").find("div").css("line-height", "0%")
            }
        });
        AtKit.addButton("fontSettings", AtKit.localisation("fonts_dialogTitle"), "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/baseline-text_fields-black-18/1x/baseline_text_fields_black_18dp.png", function(a) {
            AtKit.message(a.main);
            $lib("#ATApplyFont").click(function() {
                AtKit.call("changeFont", {
                    fontFace: $lib("#sbfontface").val(),
                    lineHeight: $lib("#sblinespacing").val()
                });
                 window.localStorage.setItem("fFace", $lib("#sbfontface").val());
            });
            $lib("#sbfontface").focus()
        }, d, null)
    };
    "undefined" == typeof window.AtKit ? (window.AtKitLoaded = function() {
            var d = null;
            this.subscribe = function(a) {
                d = a
            };
            this.fire = function(a, c) {
                null != d && d(a, c)
            }
        }, window.AtKitLoaded =
        new AtKitLoaded, window.AtKitLoaded.subscribe(function() {
            AtKit.registerPlugin("fonts", e)
        })) : AtKit.registerPlugin("fonts", e)
})();

$( document ).ready(function() {
    if(localStorage.fFace != undefined){
    setTimeout(function(){ 
        AtKit.call("changeFont", {
            fontFace: localStorage.fFace,
        });
    }, 3000);
    }
});