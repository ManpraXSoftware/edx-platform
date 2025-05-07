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
            // Manprax
        // MathJax.Hub.Config({
        //     tex2jax: {
        //         inlineMath: [
        //             ['\\(', '\\)'],
        //             ['[mathjaxinline]', '[/mathjaxinline]']
        //         ],
        //         displayMath: [
        //             ['\\[', '\\]'],
        //             ['[mathjax]', '[/mathjax]']
        //         ]
        //     }
        // });

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
            // Manprax
            // MathJax.Hub.processSectionDelay = 0;
            MathJax.processSectionDelay = 0;

        }
        // Manprax
        // MathJax.Hub.signal.Interest(function(message) {
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
    // Manprax
    // window.MathJax = {
    //     menuSettings: {
    //         collapsible: true,
    //         autocollapse: false,
    //         explorer: true
    //     }
    // };
    window.MathJax.menuSettings=  {
        collapsible: true,
        autocollapse: false,
        explorer: true
};
    // Manprax
    // vendorScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@2.7.5/MathJax.js?config=TeX-MML-AM_HTMLorMML';
    vendorScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
    document.body.appendChild(vendorScript);
}
