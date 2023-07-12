window.addEventListener("load", function () {
  django.jQuery(document).ready(function () {
    django.jQuery("span.field-off").parent("td").addClass("field-off");
  });
});
