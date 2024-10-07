(function() {
    var e = function() {
        $lib = AtKit.lib();
        AtKit.addLocalisationMap("en", {
            resize_up: "Increase Font Size",
            resize_down: "Decrease Font Size"
        });
        AtKit.addLocalisationMap("ar", {
            resize_up: "&#1578;&#1603;&#1576;&#1610;&#1585; &#1581;&#1580;&#1605; &#1575;&#1604;&#1582;&#1591;",
            resize_down: "&#1578;&#1589;&#1594;&#1610;&#1585; &#1581;&#1580;&#1605; &#1575;&#1604;&#1582;&#1591;"
        });
        AtKit.addFn("resizeText", function(d) {
            if(window.localStorage.getItem("fSize") === null)
            {
              var l = 0;
            }
            else {
              var l = window.localStorage.getItem("fSize");
            }
           for (var b = AtKit.getHtmlTags(), a = 0; a < b.length; a++) $lib(b[a]).each(function(b, c) {
                if (!$lib(c).is("#sbar") &&
                    !$lib(c).is("#sbar *") && !$lib(c).is("body > .tooltip") && !$lib(c).is("body > .tooltip *")) {
                    var a = $lib(c).css("font-size"),
                    a = parseFloat(a);
                    e = parseFloat(d);
                    newVal = parseFloat(a + e)
                } else newVal = $lib(c).css("font-size");
                $lib(c).css("font-size", newVal + "px");
              })
            l = parseFloat(l);
            l = parseFloat(l+e);
            window.localStorage.setItem("fSize", l);
        });
        AtKit.addButton("resizeUp", AtKit.localisation("resize_up"), "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/icons8-add-new-24_1.png", function() {
            AtKit.call("resizeText", "1")
        }, null, null);
        AtKit.addButton("resizeDown", AtKit.localisation("resize_down"), "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/icons8-minus-32_1.png",
            function() {
                AtKit.call("resizeText", "-1")
            }, null, null);
    };
    
    "undefined" == typeof window.AtKit ? (window.AtKitLoaded = function() {
        var d = null;
        this.subscribe = function(b) {
            d = b
        };
        this.fire = function(b, a) {
            null != d && d(b, a)
        }
    }, window.AtKitLoaded = new AtKitLoaded, window.AtKitLoaded.subscribe(function() {
        AtKit.registerPlugin("resize", e)
    })) : AtKit.registerPlugin("resize", e)
})();

$( document ).ready(function() {
    if(localStorage.fSize != undefined){
    setTimeout(function(){ 
            if(Number(localStorage.fSize)>0){
                AtKit.call("resizeText", "1")
             }else{
                 AtKit.call("resizeText", "-1")
             }
    }, 3000);
    }
});
