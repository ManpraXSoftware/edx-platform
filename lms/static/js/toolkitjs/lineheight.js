(function() {
    var t = function() {
        $lib = AtKit.lib();
        AtKit.addLocalisationMap("en", {
            fonts_dialogTitle: "Page Line Spacing Settings",
            //fonts_fontFace: "Font Face",
            fonts_lineSpacing: "Line Spacing",
            fonts_apply: "Apply"
        });
        AtKit.addLocalisationMap("ar", {
            fonts_dialogTitle: "&#1575;&#1604;&#1578;&#1581;&#1603;&#1605; &#1601;&#1610; &#1606;&#1608;&#1593; &#1575;&#1604;&#1582;&#1591;",
            fonts_fontFace: "&#1606;&#1608;&#1593; &#1575;&#1604;&#1582;&#1591;",
            fonts_lineSpacing: "&#1575;&#1604;&#1605;&#1587;&#1575;&#1601;&#1575;&#1578; &#1576;&#1610;&#1606; &#1575;&#1604;&#1571;&#1587;&#1591;&#1585;",
            fonts_apply: "&#1578;&#1591;&#1576;&#1610;&#1602;"
        });
        var s = {
            main: "<h1>" + AtKit.localisation("fonts_dialogTitle") + '</h1><br /><br /> <label for="sblinespacing">' +
                AtKit.localisation("fonts_lineSpacing") + '</label> <input type="text" name="sblinespacing" id="sblinespacing" maxlength="3" size="3" value="100">%<br /><br /><button id="ATApplyFont">' + AtKit.localisation("fonts_apply") + "</a></div>"
        };
        AtKit.addFn("changeFont", function(p) {
            var r = AtKit.getHtmlTags();
            if ("--Site Specific--" != p.fontFace) {
                for (var q = 0; q < r.length; q++) $lib(r[q]).css("font-family", p.fontFace);
                for (q = 0; q < r.length; q++) $lib(r[q]).css("line-height", p.lineHeight + "%");
                $lib("#sbar").find("div").css("line-height",
                    "0%")
            }
        });
        AtKit.addButton("fontSettings1", AtKit.localisation("fonts_dialogTitle"), "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/baseline-format_line_spacing-black-18/1x/baseline_format_line_spacing_black_18dp.png", function(p) {
            AtKit.message(p.main);
            $lib("#ATApplyFont").click(function() {
                AtKit.call("changeFont", {
                    fontFace: $lib("#sbfontface").val(),
                    lineHeight: $lib("#sblinespacing").val()
                });
                 window.localStorage.setItem("lHeight", $lib("#sblinespacing").val());
            });
            $lib("#sbfontface").focus()
        }, s, null)
    };
    "undefined" == typeof window.AtKit ? (window.AtKitLoaded = function() {
            var s = null;
            this.subscribe = function(a) {
                s = p
            };
            this.fire = function(p, r) {
                null != s && s(p, r)
            }
        }, window.AtKitLoaded =
        new AtKitLoaded, window.AtKitLoaded.subscribe(function() {
            AtKit.registerPlugin("fonts1", t)
        })) : AtKit.registerPlugin("fonts1", t)
})();


$( document ).ready(function() {
    if(localStorage.fFace != undefined){
    setTimeout(function(){ 
        AtKit.call("changeFont", {
            lineHeight: localStorage.lHeight,
        });
    }, 3000);
    }
});