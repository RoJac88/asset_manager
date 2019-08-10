$(document).ready(function() {

  $('.select-cls').each( function() {
    var index = this.id.split('-')[1];
    var target_id = this.id.split('-')[0]+'-'+index+'-target_attr';
    $('#'+target_id).empty();
    $.getJSON($SCRIPT_ROOT + '/_get_entries', {
      target: this.value,
    }, function(data) {
      $.each(data, function( index, value ) {
        console.log(value);
        $('#'+target_id).append(new Option(value, value));
        });
    });
  });

  $('.select-cls').on('change', function() {
    var index = this.id.split('-')[1]
    var target_id = this.id.split('-')[0]+'-'+index+'-target_attr'
    $('#'+target_id).empty();
    $.getJSON($SCRIPT_ROOT + '/_get_entries', {
      target: this.value,
    }, function(data) {
      $.each(data, function( index, value ) {
        console.log(value);
        $('#'+target_id).append(new Option(value, value));
        });
    });
  });
});
