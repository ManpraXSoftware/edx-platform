(function() {
    var g = function() {
        $lib = AtKit.lib();
        AtKit.addLocalisationMap("en", {
            tts_title: "Text to Speech",
            tts_options: "Text to Speech Options",
            tts_converting: "Text to Speech conversion is taking place.",
            tts_timeremaining: "Time Remaining:",
            tts_pleasewait: "Please wait...",
            tts_playpause: "Play / Pause",
            tts_rewind: "Rewind",
            tts_stop: "Stop & Close TTS",
            tts_error: "Error",
            tts_overloaded: "The server is currently over capacity for text to speech conversions. Please try again later.",
            tts_problem: "Something went wrong while we were converting this page to speech. Please try again shortly.",
            tts_servererror: "An error occurred on the server. Please try again later.",
            tts_seconds: "seconds",
            tts_explain: "To use the text to speech feature with selected text, please first select the text on this page that you would like to convert. After you have done this, click the Text to Speech button, and select the 'selected text' option.",
            tts_select_voice: "Highlight text and select a voice",
            tts_male: "Male",
            tts_female: "Female"
        });
        AtKit.addLocalisationMap("ar", {
            tts_title: "&#1578;&#1581;&#1608;&#1610;&#1604; &#1575;&#1604;&#1606;&#1589;&#1608;&#1589; &#1575;&#1604;&#1610; &#1605;&#1575;&#1583;&#1577; &#1605;&#1587;&#1605;&#1608;&#1593;&#1577;",
            tts_options: "&#1582;&#1610;&#1575;&#1585;&#1575;&#1578; &#1606;&#1591;&#1602; &#1575;&#1604;&#1606;&#1589;",
            tts_converting: "&#1580;&#1575;&#1585;&#1610;&#1577; &#1581;&#1575;&#1604;&#1610;&#1575;&#1611; &#1593;&#1605;&#1604;&#1610;&#1577; &#1606;&#1591;&#1602; &#1575;&#1604;&#1606;&#1589;",
            tts_timeremaining: "&#1575;&#1604;&#1608;&#1602;&#1578; &#1575;&#1604;&#1605;&#1578;&#1576;&#1602;&#1610;",
            tts_pleasewait: "&#1575;&#1604;&#1585;&#1580;&#1575;&#1569; &#1575;&#1604;&#1575;&#1606;&#1578;&#1592;&#1575;&#1585;...",
            tts_playpause: "&#1578;&#1588;&#1594;&#1610;&#1604;/&#1573;&#1610;&#1602;&#1575;&#1601; &#1605;&#1572;&#1602;&#1578;",
            tts_rewind: "&#1573;&#1593;&#1575;&#1583;&#1577;",
            tts_stop: "&#1573;&#1610;&#1602;&#1575;&#1601;",
            tts_error: "&#1582;&#1591;&#1571;",
            tts_overloaded: "&#1601;&#1575;&#1602;&#1578; &#1593;&#1605;&#1604;&#1610;&#1575;&#1578; &#1606;&#1591;&#1602; &#1575;&#1604;&#1606;&#1589;&#1608;&#1589; &#1587;&#1593;&#1577; &#1575;&#1604;&#1582;&#1575;&#1583;&#1605;. &#1575;&#1604;&#1585;&#1580;&#1575;&#1569; &#1575;&#1604;&#1605;&#1581;&#1575;&#1608;&#1604;&#1577; &#1604;&#1575;&#1581;&#1602;&#1575;&#1611;.",
            tts_problem: "&#1581;&#1583;&#1579; &#1582;&#1591;&#1571; &#1571;&#1579;&#1606;&#1575;&#1569; &#1593;&#1605;&#1604;&#1610;&#1577; &#1606;&#1591;&#1602; &#1575;&#1604;&#1589;&#1601;&#1581;&#1577;. &#1575;&#1604;&#1585;&#1580;&#1575;&#1569; &#1575;&#1604;&#1605;&#1581;&#1575;&#1608;&#1604;&#1577; &#1576;&#1593;&#1583; &#1602;&#1604;&#1610;&#1604;.",
            tts_servererror: "&#1581;&#1583;&#1579; &#1582;&#1591;&#1571; &#1601;&#1610; &#1575;&#1604;&#1582;&#1575;&#1583;&#1605;. &#1575;&#1604;&#1585;&#1580;&#1575;&#1569; &#1575;&#1604;&#1605;&#1581;&#1575;&#1608;&#1604;&#1577; &#1604;&#1575;&#1581;&#1602;&#1575;&#1611;.",
            tts_seconds: "&#1579;&#1608;&#1575;&#1606;&#1613;",
            tts_explain: "&#1604;&#1575;&#1587;&#1578;&#1582;&#1583;&#1575;&#1605; &#1582;&#1575;&#1589;&#1610;&#1577; &#1606;&#1591;&#1602; &#1575;&#1604;&#1606;&#1589;&#1548; &#1575;&#1604;&#1585;&#1580;&#1575;&#1569; &#1578;&#1581;&#1583;&#1610;&#1583; &#1575;&#1604;&#1606;&#1589; &#1575;&#1604;&#1605;&#1585;&#1575;&#1583; &#1578;&#1581;&#1608;&#1610;&#1604;&#1607; &#1593;&#1604;&#1609; &#1607;&#1584;&#1607; &#1575;&#1604;&#1589;&#1601;&#1581;&#1577;. &#1576;&#1593;&#1583; &#1584;&#1604;&#1603; &#1575;&#1590;&#1594;&#1591; &#1586;&#1585; &#1606;&#1591;&#1602; &#1575;&#1604;&#1606;&#1589;&#1548; &#1608;&#1575;&#1590;&#1594;&#1591; &#1582;&#1610;&#1575;&#1585; &quot;&#1575;&#1604;&#1606;&#1589; &#1575;&#1604;&#1605;&#1581;&#1583;&#1583;&quot;.",
            tts_select_voice: "&#1602;&#1605; &#1576;&#1578;&#1592;&#1604;&#1610;&#1604; &#1575;&#1604;&#1606;&#1589; &#1608;&#1575;&#1582;&#1578;&#1610;&#1575;&#1585; &#1575;&#1604;&#1589;&#1608;&#1578;",
            tts_male: "&#1605;&#1584;&#1603;&#1585;",
            tts_female: "&#1605;&#1572;&#1606;&#1579;"
        });
        var f = {
            options: {
                title: AtKit.localisation("tts_options"),
                body: AtKit.localisation("tts_select_voice") + ' <br /></button> <button id="sbStartInsipioTTSSelectionFemale"> ' +
                    AtKit.localisation("tts_female") + "</button>"
            },
            starting: {
                title: AtKit.localisation("tts_title"),
                body: "<center>" + AtKit.localisation("tts_converting") + " <br /><img src='" + AtKit.getPluginURL() + "images/loadingbig.gif' /><br />" + AtKit.localisation("tts_timeremaining") + " <div id='sbttstimeremaining'>...</div><br />" + AtKit.localisation("tts_pleasewait") + " </center>"
            }
        };
        AtKit.addFn("getSelectedTextInsipioTTS", function(b) {
            var c = AtKit.call("getSelectedTextInElementInsipio");
            null == c && (c = "", document.selection &&
                "Control" != document.selection.type && "" != document.selection.createRange().text ? c = document.selection.createRange().text : window.getSelection && "" != window.getSelection().toString() ? c = window.getSelection().toString() : document.getSelection && (c = document.getSelection()));
            return !0 === b ? String(c).replace(/([\s]+)/ig, "") : String(c)
        });
        AtKit.addFn("getSelectedTextInElementInsipio", function() {
            var b = document.activeElement;
            return ("selectionStart" in b && function() {
                return b.value.substr(b.selectionStart, b.selectionEnd -
                    b.selectionStart)
            } || document.selection && function() {
                var c = $lib(b).prop("nodeName");
                if ("input" != c && "textarea" != c) return null;
                b.focus();
                c = document.selection.createRange();
                if (null === c) return null;
                var e = b.createTextRange(),
                    d = e.duplicate();
                e.moveToBookmark(c.getBookmark());
                d.setEndPoint("EndToStart", e);
                return c.text
            } || function() {
                return null
            })()
        });
        AtKit.addFn("b64", function(b) {
            for (var c = "", e, d, f, g, j, h, i = 0, b = AtKit.call("utf8_encode", b); i < b.length;) e = b.charCodeAt(i++), d = b.charCodeAt(i++), f = b.charCodeAt(i++),
                g = e >> 2, e = (e & 3) << 4 | d >> 4, j = (d & 15) << 2 | f >> 6, h = f & 63, isNaN(d) ? j = h = 64 : isNaN(f) && (h = 64), c = c + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-=".charAt(g) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-=".charAt(e) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-=".charAt(j) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-=".charAt(h);
            return c
        });
        AtKit.addFn("utf8_encode", function(b) {
            for (var b = b.replace(/\r\n/g, "\n"), c = "", e = 0; e < b.length; e++) {
                var d =
                    b.charCodeAt(e);
                128 > d ? c += String.fromCharCode(d) : (127 < d && 2048 > d ? c += String.fromCharCode(d >> 6 | 192) : (c += String.fromCharCode(d >> 12 | 224), c += String.fromCharCode(d >> 6 & 63 | 128)), c += String.fromCharCode(d & 63 | 128))
            }
            return c
        });
        AtKit.addFn("sendInsipioTTSChunk", function(b) {
            var c = 1 == b.block ? 0 : 400 * b.block,
                c = b.fullData.substring(c, c + 400 > b.fullData.length ? b.fullData.length : c + 400),
                c = "https://speech.services.atbar.org/insipio-tts/request.php?rt=tts&v=2&i=1&l=" + AtKit.getLanguage() + "&voice=" + b.voice + "&id=" + b.reqID + "&data=" +
                c + "&chunkData=" + b.totalBlocks + "-" + b.block;
            b.block == b.totalBlocks - 1 && (c += "&page=" + encodeURIComponent(window.location));
            $lib.getJSON(c + "&callback=?", function(c) {
                $lib("#compactStatus").html(b.block + " / " + b.totalBlocks);
                var d = "<h2>" + AtKit.localisation("tts_error") + "</h2>";
                b.block == b.totalBlocks ? (AtKit.show(f.starting), "encoding" == c.status ? AtKit.call("countdownInsipioTTS", {
                    timeLeft: c.est_completion / c.chunks,
                    id: c.ID
                }) : "failure" == c.status && "overcapacity" == c.reason ? AtKit.message(d + "<p>" + AtKit.localisation("tts_overloaded") +
                    "</p>") : "failure" == c.status && "" === c.message ? AtKit.message(d + "<p>" + AtKit.localisation("tts_problem") + "</p>") : AtKit.message(d + "<p>" + c.reason + " " + c.data.message + "</p>")) : "ChunkSaved" == c.data.message ? AtKit.call("sendInsipioTTSChunk", {
                    fullData: b.fullData,
                    block: b.block + 1,
                    totalBlocks: b.totalBlocks,
                    reqID: b.reqID
                }) : AtKit.message(d + "<p>" + AtKit.localisation("tts_servererror") + "</p>")
            })
        });
        AtKit.addFn("countdownInsipioTTS", function(b) {
            isNaN(b.timeLeft) ? AtKit.message("<h2>" + AtKit.localisation("tts_error") + "</h2> <p>" +
                AtKit.localisation("tts_problem") + "</p>") : 0 == b.timeLeft ? ("msie" != $lib.browser ? a.canPlayType && a.canPlayType("audio/mpeg").replace(/no/, "") ? (chunkUrls = [], $lib.getJSON("https://speech.services.atbar.org/cache/request.php?id=" + b.id + "&callback=?").done(function(b) {
                    index = 0;
                    $lib.isArray(b.trackList.track) ? $lib.each(b.trackList.track, function(b, c) {
                        audioURL = c.location;
                        chunkUrls.push(audioURL)
                    }) : chunkUrls.push(b.trackList.track.location);
                    AtKit.call("playChunksHtml5", {
                        chunkUrls: chunkUrls,
                        index: 0
                    })
                }).fail(function() {
                    console.log("error")
                })) :
                ($lib("body").append($lib('<div id="flashContent"><OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" width="1" height="1" id="audioe"> <PARAM name=movie value="https://speech.services.atbar.org/lib/player/player-licensed.swf"></PARAM> <PARAM name=flashvars value="file=https://speech.services.atbar.org/cache/' + b.id + '.xml&autostart=true&playlist=bottom&repeat=list&playerready=playerReady&id=audioo"><PARAM name=allowscriptaccess value="always" /><embed type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" src="https://speech.services.atbar.org/lib/player/player-licensed.swf" width="1" height="1" allowscriptaccess="always" allowfullscreen="false" flashvars="file=https://speech.services.atbar.org/cache/' +
                    b.id + '.xml&autostart=true&playlist=bottom&repeat=list&playerready=playerReady" name="audioe" /> </OBJECT></div>')), AtKit.call("setupInsipioTTSListeners")) : ($lib("<div />", {
                    id: "flashContent"
                }).prependTo("body"), swfobject.embedSWF("https://speech.services.atbar.org/lib/player/player-licensed.swf", "flashContent", "1", "1", "9.0.0", "expressInstall.swf", !1, {
                    flashvars: "file=https://speech.services.atbar.org/cache/" + b.id + ".xml&autostart=true&playlist=bottom&repeat=list&playerready=playerReady&id=audioo",
                    allowscriptaccess: "always"
                }, {
                    id: "audioo",
                    name: "audioo"
                }, function() {
                    AtKit.call("setupInsipioTTSListeners")
                })), AtKit.hideDialog()) : ($lib("#sbttstimeremaining").html(b.timeLeft + " " + AtKit.localisation("tts_seconds")), window.setTimeout(function() {
                AtKit.call("countdownInsipioTTS", {
                    timeLeft: b.timeLeft - 1,
                    id: b.id
                })
            }, 1E3))
        });
        AtKit.addFn("setupInsipioTTSListeners", function() {
            !0 != AtKit.get("TTS_Listeners_setup") && (window.playerReady = function(b) {
                AtKit.set("ATAudioPlayerID", b.id);
                AtKit.set("TTS_position", 0);
                AtKit.set("TTS_playingItem", 0);
                b = swfobject.getObjectById(b.id);
                "msie" != $lib.browser && (b = window.document.audioe);
                b.addModelListener("STATE", "ATBarAudioStateListener");
                b.addModelListener("TIME", "ATBarAudioTimeMonitor");
                b.addControllerListener("ITEM", "ATBarAudioItemMonitor")
            }, window.ATBarAudioTimeMonitor = function(b) {
                AtKit.set("TTS_position", b.position)
            }, window.ATBarAudioItemMonitor = function(b) {
                AtKit.set("TTS_playingItem", b.index)
            }, window.ATBarAudioStateListener = function(b) {
                var c = b.newstate,
                    b = swfobject.getObjectById(b.id);
                "msie" !=
                $lib.browser && (b = window.document.audioe);
                "COMPLETED" == c && AtKit.get("TTS_playingItem") + 1 == b.getPlaylist().length && AtKit.call("TTSRemoveControlBox");
                "IDLE" == c || "PAUSED" == c ? ($lib("#at-lnk-ttsPlay").children("img").attr("src", AtKit.getPluginURL() + "images/control.png"), $lib("#at-btn-tts").children("img").attr("src", "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/baseline-mic-black-18/1x/baseline_mic_black_18dp.png").css("padding-top", "6px")) : !1 == AtKit.get("TTS_clickEnabled") && ($lib("#at-lnk-ttsPlay").children("img").attr("src", AtKit.getPluginURL() + "images/control-pause.png"),
                    $lib("#at-btn-tts").children("img").attr("src", AtKit.getPluginURL() + "images/loading.gif").css("padding-top", "8px"))
            }, AtKit.set("TTS_Listeners_setup", !0))
        });
        AtKit.addFn("TTSRemoveControlBox", function() {
            AtKit.removeButton("ttsPlay");
            AtKit.removeButton("ttsRewind");
            AtKit.removeButton("ttsStop");
            $lib("#flashContent").remove();
            $lib("#at-lnk-tts").children("img").attr("src", "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/baseline-mic-black-18/1x/baseline_mic_black_18dp.png").css("padding-top", "6px");
            AtKit.set("TTS_clickEnabled", !0)
        });
        AtKit.addFn("sbStartInsipioTTSSelection",
            function(b) {
                AtKit.set("TTS_clickEnabled", !1);
                var c = AtKit.get("TTSselectedData");
                if ("" == c || "undefined" == typeof c) c = AtKit.call("getSelectedTextInsipioTTS");
                if ("undefined" != typeof c && "" !== c) {
                    this.clickEnabled = !1;
                    var c = AtKit.call("b64", c),
                        e = Math.ceil(c.length / 400);
                    if (0 < e) {
                        var d = Math.floor(5001 * Math.random());
                        AtKit.message("<h2>" + AtKit.localisation("tts_pleasewait") + "</h2><p>" + AtKit.localisation("tts_converting") + "...<br /><div id='compactStatus'>0 / " + e + "</div></p>");
                        AtKit.call("sendInsipioTTSChunk", {
                            fullData: c,
                            block: 1,
                            totalBlocks: e,
                            reqID: d,
                            voice: b.voice
                        })
                    } else AtKit.message("<h2>" + AtKit.localisation("tts_error") + "</h2><p>" + AtKit.localisation("tts_problem") + "</p>")
                } else AtKit.message("<h2>" + AtKit.localisation("tts_title") + "</h2><p>" + AtKit.localisation("tts_explain") + "</p>")
            });
        AtKit.addFn("playChunksHtml5", function(b) {
            chunkUrls = b.chunkUrls;
            index = b.index;
            chunkUrls[index] && (audio.src = chunkUrls[index], audio.load(), audio.play(), chunkUrls[index + 1] && audio.addEventListener("ended", function() {
                AtKit.call("playChunksHtml5", {
                    chunkUrls: chunkUrls,
                    index: index + 1
                })
            }))
        });
        AtKit.set("TTS_clickEnabled", !0);
        $lib(document).delegate("#at-btn-tts", "mousemove, focus, mouseover", function() {
            var b = AtKit.call("getSelectedTextInsipioTTS");
            "undefined" == typeof b || "" == b || AtKit.set("TTSselectedData", b)
        });
        AtKit.addButton("tts", AtKit.localisation("tts_title"), "https://cdn.jsdelivr.net/gh/suprgyabhushan/my-style-theme/lms/static/images/baseline-mic-black-18/1x/baseline_mic_black_18dp.png", function(b) {
            if (!1 != AtKit.set("TTS_clickEnabled")) {
                var c = AtKit.call("getSelectedTextInsipioTTS");
                "" == AtKit.get("TTSselectedData") && "" != c && AtKit.set("TTSselectedData",
                    c);
                AtKit.show(b.options);
                AtKit.set("TTS_Listeners_setup", !1);
                AtKit.addScript("https://core.atbar.org/resources/js/swfobject.js", null);
                $lib("#sbStartInsipioTTSSelectionMale").on("click touchend", function() {
                    a = document.createElement("audio");
                    audio = new Audio;
                    audio.play();
                    audio.pause();
                    AtKit.call("sbStartInsipioTTSSelection", {
                        voice: "male"
                    })
                });
                $lib("#sbStartInsipioTTSSelectionFemale").on("click touchend", function() {
                    a = document.createElement("audio");
                    audio = new Audio;
                    audio.play();
                    audio.pause();
                    AtKit.call("sbStartInsipioTTSSelection", {
                        voice: "female"
                    })
                })
            }
        }, f, {});
        navigator.userAgent.match(/(iPhone|iPod|iPad)/i) && setInterval(function() {
            AtKit.call("getSelectedTextInsipioTTS")
        }, 100);
        $lib("a#at-lnk-tts").on("click touchend", function() {
            AtKit.call("getSelectedTextInsipioTTS");
            navigator.userAgent.match(/(iPhone|iPod|iPad)/i)
        })
    };
    "undefined" == typeof window.AtKit ? (window.AtKitLoaded = function() {
        var f = null;
        this.subscribe = function(b) {
            f = b
        };
        this.fire = function(b, c) {
            null !== f && f(b, c)
        }
    }, window.AtKitLoaded = new AtKitLoaded, window.AtKitLoaded.subscribe(function() {
        AtKit.registerPlugin("insipio-tts",
            g)
    })) : AtKit.registerPlugin("insipio-tts", g)
})();