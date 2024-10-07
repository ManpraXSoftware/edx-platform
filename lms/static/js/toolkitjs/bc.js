(function() {
    var w = function() {
        $lib = AtKit.lib();
        AtKit.addLocalisationMap("en", {
            css_title: "Change Background Colour",
            css_changeColour: "Change Colour Settings",
            css_changePage: "Change Background Color",
            css_change_page: "Change Background Colour",
            css_black_colour: "Black",
            css_red_colour: "Red",
            css_yellow_colour: "Yellow",
            css_green_colour: "Green",
            css_grey_colour: "Grey",
            css_blue_colour: "Blue"
        });
        var v = '<option value="original">--' + AtKit.localisation("css_colour_original") + '--</option><option value="B80028">' + AtKit.localisation("css_colour_red") + '</option><option value="194E84">' + AtKit.localisation("css_colour_blue") + '</option><option value="60BB22">' + AtKit.localisation("css_colour_green") + '</option><option value="FDB813">' + AtKit.localisation("css_colour_yellow") + '</option><option value="F17022">' + AtKit.localisation("css_colour_orange") + '</option><option value="000000">' + AtKit.localisation("css_black") +
            '</option><option value="A8B1B8">' + AtKit.localisation("css_grey") + '</option><option value="FFFFFF">' + AtKit.localisation("css_white") + "</option>",
            v = {
              main: {
                  title: AtKit.localisation("css_changeColour"),
                  body: '<button id="sbAttachCSSStyle">' + AtKit.localisation("css_changePage") + "</button>"
              },
              CSSStyles: {
                  title: AtKit.localisation("css_change_page"),
                  body: '<button id="sbApplyCSS-b" style="background: black; width:36%">' + AtKit.localisation("css_black_colour") + '</button><br /> <button id="sbApplyCSS-r" style="background: red; width:36%">' + AtKit.localisation("css_red_colour") + '</button><br /> <button id="sbApplyCSS-y" style="background: yellow; width:36%">' + AtKit.localisation("css_yellow_colour") + '</button><br /> <button id="sbApplyCSS-blue" style="background: blue; width:36%">' + AtKit.localisation("css_blue_colour") +
                      '</button><br /> <button id="sbApplyCSS-green" style="background: green; width:36%">' + AtKit.localisation("css_green_colour") + '</button><br /> <button id="sbApplyCSS-grey" style="background: grey; width:36%">' + AtKit.localisation("css_grey_colour") + '</button>'
              }
            };
        CSSFunctions = {
            CSSStyles: function() {
                $lib("#sbApplyCSS-y").click(function() {
                    a = '<div id="bcsession" class="at-overlay" style="background-color:#BABA70; opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
                    $lib(".at-overlay").remove();
                    $lib("body").prepend(a);
                    window.localStorage.setItem("bColour", "#BABA70")
                });
                $lib("#sbApplyCSS-b").click(function() {
                  a = '<div id="bcsession" class="at-overlay" style="background-color:black; opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
                  $lib(".at-overlay").remove();
                  $lib("body").prepend(a);
                  window.localStorage.setItem("bColour", "black")
                });
                $lib("#sbApplyCSS-r").click(function() {
                  a = '<div id="bcsession" class="at-overlay" style="background-color:#FF6699; opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
                  $lib(".at-overlay").remove();
                  $lib("body").prepend(a);
                  window.localStorage.setItem("bColour", "#FF6699")
                });
                $lib("#sbApplyCSS-blue").click(function() {
                  a = '<div id="bcsession" class="at-overlay" style="background-color:#3399CC; opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
                  $lib(".at-overlay").remove();
                  $lib("body").prepend(a);
                  window.localStorage.setItem("bColour", "#3399CC")
                });
                $lib("#sbApplyCSS-green").click(function() {
                  a = '<div id="bcsession" class="at-overlay" style="background-color:#00CC66; opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
                  $lib(".at-overlay").remove();
                  $lib("body").prepend(a);
                  window.localStorage.setItem("bColour", "#00CC66")
                });
                $lib("#sbApplyCSS-grey").click(function() {
                  a = '<div id="bcsession" class="at-overlay" style="background-color:#808080; opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
                  $lib(".at-overlay").remove();
                  $lib("body").prepend(a);
                  window.localStorage.setItem("bColour", "#808080")
                });
                $lib("#sbApplyCSS-b").focus()
            }
        };
        AtKit.addButton("back", AtKit.localisation("css_title"), "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/baseline_palette_black_18dp.png", function(u, v) {
            AtKit.show(u.CSSStyles);
            v.CSSStyles()
            $lib("#sbAttachCSSStyle").click(function() {
                AtKit.show(u.CSSStyles);
                v.CSSStyles()
            })
        }, v, CSSFunctions)
    };
    "undefined" == typeof window.AtKit ? (window.AtKitLoaded =
        function() {
            var v = null;
            this.subscribe = function(u) {
                v = u
            };
            this.fire = function(u, w) {
                null != v && v(u, w)
            }
        }, window.AtKitLoaded = new AtKitLoaded, window.AtKitLoaded.subscribe(function() {
            AtKit.registerPlugin("back", w)
        })) : AtKit.registerPlugin("back", w)
})();

$( document ).ready(function() {
    if(localStorage.bColour != undefined){
    setTimeout(function(){ 
        a ='<div id="bcsession" class="at-overlay" style="background-color:'+localStorage.bColour+' ;opacity:0.4; position:absolute; top:0; left:0; height:100%; width:100%; z-index:2147483640; opacity:0.3; filter: alpha(opacity = 30); pointer-events: none; position:fixed"></div>';
        $lib(".at-overlay").remove();
        $lib("body").prepend(a);
    }, 2000);
    }
});