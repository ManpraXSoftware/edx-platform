(function() {
    var h = function() {
        $lib = AtKit.lib();
        AtKit.addLocalisationMap("en", {
            css_title: "Change Link Colours",
            css_changeColour: "Change Link Colours",
            //css_changeToolbar: "Change Toolbar colour",
            css_changeText: "Change Link Colours",
            //css_changePage: "Change background color",
            //css_changeATbar: "Change ATbar colour",
            //css_changeBackground: "Background colour",
            //css_set: "Set",
            css_black: "Black",
            css_white: "White",
            css_grey: "Grey",
            //css_random: "Random",
            //css_reset_defaults: "Reset to Defaults",
            css_change_linktext: "Change Link Colours",
            css_textcolour: "Text Colour:",
            css_colour_original: "Original",
            css_colour_red: "Red",
            css_colour_blue: "Blue",
            css_colour_green: "Green",
            css_colour_yellow: "Yellow",
            css_colour_orange: "Orange",
            css_linkColour: "Link Colour:",
            css_apply: "Apply",
            //css_change_page: "Change Background Colour",
            //css_black_colour: "Black",
            //css_red_colour: "Red",
            //css_yellow_colour: "Yellow",
            //css_green_colour: "Green",
            //css_grey_colour: "Grey",
            //css_blue_colour: "Blue"
        });
        AtKit.addLocalisationMap("ar", {
            css_title: "&#1575;&#1604;&#1578;&#1581;&#1603;&#1605; &#1601;&#1610; &#1605;&#1592;&#1607;&#1585; &#1575;&#1604;&#1589;&#1601;&#1581;&#1577;  &#1575;&#1604;&#1581;&#1575;&#1604;&#1610;&#1577;",
            css_changeColour: "&#1573;&#1593;&#1583;&#1575;&#1583;&#1575;&#1578; &#1578;&#1594;&#1610;&#1610;&#1585; &#1575;&#1604;&#1571;&#1604;&#1608;&#1575;&#1606;",
            css_changeToolbar: "&#1578;&#1594;&#1610;&#1610;&#1585; &#1604;&#1608;&#1606; &#1588;&#1585;&#1610;&#1591; &#1575;&#1604;&#1571;&#1583;&#1608;&#1575;&#1578;",
            css_changeText: "&#1578;&#1594;&#1610;&#1610;&#1585; &#1571;&#1604;&#1608;&#1575;&#1606; &#1575;&#1604;&#1606;&#1589;&#1608;&#1589; &#1608;&#1575;&#1604;&#1585;&#1608;&#1575;&#1576;&#1591;",
            css_changePage: "&#1578;&#1594;&#1610;&#1610;&#1585; &#1606;&#1605;&#1591; &#1575;&#1604;&#1589;&#1601;&#1581;&#1577;",
            css_changeATbar: "&#1578;&#1594;&#1610;&#1610;&#1585; &#1604;&#1608;&#1606;  ATbar",
            css_changeBackground: "&#1604;&#1608;&#1606; &#1575;&#1604;&#1582;&#1604;&#1601;&#1610;&#1577;",
            css_set: "&#1578;&#1591;&#1576;&#1610;&#1602;",
            css_black: "&#1571;&#1587;&#1608;&#1583;",
            css_white: "&#1571;&#1576;&#1610;&#1590;",
            css_grey: "&#1585;&#1605;&#1575;&#1583;&#1610;",
            css_random: "&#1593;&#1588;&#1608;&#1575;&#1574;&#1610;",
            css_reset_defaults: "&#1575;&#1587;&#1578;&#1593;&#1575;&#1583;&#1577; &#1575;&#1604;&#1608;&#1590;&#1593; &#1575;&#1604;&#1571;&#1589;&#1604;&#1610;",
            css_change_linktext: "&#1578;&#1594;&#1610;&#1610;&#1585; &#1571;&#1604;&#1608;&#1575;&#1606; &#1575;&#1604;&#1582;&#1591;&#1608;&#1591; &#1608;&#1575;&#1604;&#1585;&#1608;&#1575;&#1576;&#1591;",
            css_textcolour: "&#1604;&#1608;&#1606; &#1575;&#1604;&#1606;&#1589;",
            css_colour_original: "&#1575;&#1604;&#1571;&#1589;&#1604;&#1610;",
            css_colour_red: "&#1571;&#1581;&#1605;&#1585;",
            css_colour_blue: "&#1571;&#1586;&#1585;&#1602;",
            css_colour_green: "&#1571;&#1582;&#1590;&#1585;",
            css_colour_yellow: "&#1571;&#1589;&#1601;&#1585;",
            css_colour_orange: "&#1576;&#1585;&#1578;&#1602;&#1575;&#1604;&#1610;",
            css_linkColour: "&#1604;&#1608;&#1606; &#1575;&#1604;&#1585;&#1608;&#1575;&#1576;&#1591;",
            css_apply: "&#1578;&#1591;&#1576;&#1610;&#1602;",
            css_change_page: "&#1578;&#1594;&#1610;&#1610;&#1585; &#1606;&#1605;&#1591; &#1575;&#1604;&#1589;&#1601;&#1581;&#1577;",
            css_black_white: "&#1571;&#1587;&#1608;&#1583; &#1593;&#1604;&#1609; &#1582;&#1604;&#1601;&#1610;&#1577; &#1576;&#1610;&#1590;&#1575;&#1569;",
            css_white_black: "&#1571;&#1576;&#1610;&#1590; &#1593;&#1604;&#1609; &#1582;&#1604;&#1601;&#1610;&#1577; &#1587;&#1608;&#1583;&#1575;&#1569;",
            css_yellow_black: "&#1571;&#1589;&#1601;&#1585; &#1593;&#1604;&#1609; &#1582;&#1604;&#1601;&#1610;&#1577; &#1587;&#1608;&#1583;&#1575;&#1569;",
            css_black_yellow: "&#1571;&#1587;&#1608;&#1583; &#1593;&#1604;&#1609; &#1582;&#1604;&#1601;&#1610;&#1577; &#1589;&#1601;&#1585;&#1575;&#1569;",
            css_white_grey: "&#1571;&#1576;&#1610;&#1590; &#1593;&#1604;&#1609; &#1582;&#1604;&#1601;&#1610;&#1577; &#1585;&#1605;&#1575;&#1583;&#1610;&#1577;"
        });
        var g = '<option value="original">--' + AtKit.localisation("css_colour_original") + '--</option><option value="B80028">' + AtKit.localisation("css_colour_red") + '</option><option value="194E84">' + AtKit.localisation("css_colour_blue") + '</option><option value="60BB22">' + AtKit.localisation("css_colour_green") + '</option><option value="FDB813">' + AtKit.localisation("css_colour_yellow") + '</option><option value="F17022">' + AtKit.localisation("css_colour_orange") + '</option><option value="000000">' + AtKit.localisation("css_black") +
            '</option><option value="A8B1B8">' + AtKit.localisation("css_grey") + '</option><option value="FFFFFF">' + AtKit.localisation("css_white") + "</option>",
            g = {
                main: {
                    title: AtKit.localisation("css_changeColour"),
                    body: '<button id="sbChangeSiteColours"> ' + AtKit.localisation("css_changeText") + "</button>"
                },
                siteColours: {
                    title: AtKit.localisation("css_change_linktext"),
                    body: '<label for="sblinkcolour" style="display:block">' + AtKit.localisation("css_linkColour") +
                        '</label><input id ="sblinkcolour" value="fe9810" name="sblinkcolour" type="color"></input> <br /><br /><button id="applyPageColours">' + AtKit.localisation("css_apply") + "</button>"
                }
            };
        CSSFunctions = {
            siteColours: function() {
                $lib("#applyPageColours").click(function() {
                    "undefined" != $lib("#sbtextcolour").val() && "original" != $lib("#sbtextcolour").val() && $lib("*").css("color", $lib("#sbtextcolour").val());
                    "undefined" != $lib("#sblinkcolour").val() && "original" != $lib("#sblinkcolour").val() && $lib("a").css("color", $lib("#sblinkcolour").val());
                     window.localStorage.setItem("linkColour", $lib("#sblinkcolour").val());
                });
                $lib("#sblinkcolour").keypress(function(f) {
                    13 == f.keyCode && ("undefined" != $lib("#sbpagebackgroundcolour").val() && $lib("body").css("backgroundColor", $lib("#sbpagebackgroundcolour").val()), "undefined" != $lib("#sbtextcolour").val() && "original" != $lib("#sbtextcolour").val() &&
                        $lib("body").css("color", $lib("#sbtextcolour").val()), "undefined" != $lib("#sblinkcolour").val() && "original" != $lib("#sblinkcolour").val() && $lib("a").css("color", $lib("#sblinkcolour").val()), $lib(document).trigger("close.facebox"))
                });
                $lib("#sbtextcolour").focus()
            }
        };
        AtKit.addButton("link", AtKit.localisation("css_title"), "https://gitcdn.xyz/cdn/suprgyabhushan/my-style-theme/85e17dcd1df0a5678318f8b1ea0a56e15990f267/lms/static/images/baseline-link-black-18/1x/baseline_link_black_18dp.png", function(f, g) {
            AtKit.show(f.siteColours);
            g.siteColours()
           $lib("#sbChangeSiteColours").click(function() {
                AtKit.show(f.siteColours);
                g.siteColours()
            })
        }, g, CSSFunctions)
    };
    "undefined" == typeof window.AtKit ? (window.AtKitLoaded =
        function() {
            var g = null;
            this.subscribe = function(f) {
                g = f
            };
            this.fire = function(f, h) {
                null != g && g(f, h)
            }
        }, window.AtKitLoaded = new AtKitLoaded, window.AtKitLoaded.subscribe(function() {
            AtKit.registerPlugin("link", h)
        })) : AtKit.registerPlugin("link", h)
})();

$( document ).ready(function() {
    if(localStorage.linkColour != undefined){
    setTimeout(function(){ 
        "undefined" != localStorage.textColour && "original" != localStorage.textColour && $lib("*").css("color",localStorage.textColour);
        "undefined" != localStorage.linkColour && "original" != localStorage.linkColour && $lib("a").css("color",localStorage.linkColour);
    }, 3000);
    }
});