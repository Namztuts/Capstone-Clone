//alerts fade after showing up
$(document).ready(function () {
   // for each alert, fade out and close after 3 seconds
   $('.alert').each(function () {
      let alert = $(this);

      setTimeout(function () {
         alert.fadeOut(500, function () {
            $(this).alert('close'); //bootstrap alert('close')
         });
      }, 3000);
   });
});
