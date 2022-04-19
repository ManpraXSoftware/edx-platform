// See common/templates/mathjax_include.html for info on Fast Preview mode.
var disableFastPreview = true,
    vendorScript;
if (typeof MathJax === 'undefined') {
    if (disableFastPreview) {
        window.MathJax = {
            menuSettings: {CHTMLpreview: false}
        };
    }

    vendorScript = document.createElement('script');
    vendorScript.onload = function() {
        'use strict';
        var MathJax = window.MathJax,
            setMathJaxDisplayDivSettings;
        MathJax.Config({
            tex2jax: {
                inlineMath: [
                    ['\\(', '\\)'],
                    ['[mathjaxinline]', '[/mathjaxinline]']
                ],
                displayMath: [
                    ['\\[', '\\]'],
                    ['[mathjax]', '[/mathjax]']
                ]
            }
        });
        if (disableFastPreview) {
            MathJax.processSectionDelay = 0;
        }
        MathJax.signal.Interest(function(message) {
            if (message[0] === 'End Math') {
                setMathJaxDisplayDivSettings();
            }
        });
        setMathJaxDisplayDivSettings = function() {
            $('.MathJax_Display').each(function() {
                this.setAttribute('tabindex', '0');
                this.setAttribute('aria-live', 'off');
                this.removeAttribute('role');
                this.removeAttribute('aria-readonly');
            });
        };
    };
    // Automatic loading of Mathjax accessibility files
    window.MathJax.menuSettings=  {
            collapsible: true,
            autocollapse: false,
            explorer: true
    };
    vendorScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
    document.body.appendChild(vendorScript);
}
