/* JavaScript for reset option that can be done on a randomized LibraryContentBlock */
function LibraryContentReset(runtime, element) {
  $('.problem-reset-btn', element).click((e) => {
    e.preventDefault();
    $.post({
      url: runtime.handlerUrl(element, 'reset_selected_children'),
      success(data) {
        edx.HtmlUtils.setHtml(element, edx.HtmlUtils.HTML(data));
        // Rebind the reset button for the block
        XBlock.initializeBlock(element);
        // Render the new set of problems (XBlocks)
        $(".xblock", element).each(function(i, child) {
          XBlock.initializeBlock(child);
        });
      },
    });
  });

  // Manprax

  $('.check-result-btn', element).click((e) => {
    e.preventDefault();
    $.post({
      url: runtime.handlerUrl(element, 'show_user_result'),
      success(data) {
        if(data.show_reset == true && data.has_attempt == true) {
          document.getElementById("showmsg").innerHTML = "Unfortunately you do not qualify. Please reset the problem and re submit the problem.";
          document.getElementById("showmsg").style.display = "block";
          document.getElementById("btnproblemreset").style.display = "block";
        }

        if(data.show_reset == false && data.is_passed == true) {
          document.getElementById("showmsg").innerHTML = "Congratulations, you have passed.";
          document.getElementById("showmsg").style.display = "block";
        }
        
      },
    });
  });
  
}
