$().ready(function() {
    $('[data-toggle="img-modal"]').click(function(e) {
      e.preventDefault();
      var url = $(this).attr('href');
      $('<div class="modal fade"><div class="modal-dialog">' +
          '<a data-dismiss="modal"><img width=600 height=400 src="' + url + '"></a>\n' +
        '</div></div>'
      ).modal();
    });
});
