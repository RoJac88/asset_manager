$(function() {
  $("#addr_cep").on('input', function() {
    if ($(this).val().length == 8) {
      $.getJSON($SCRIPT_ROOT + '/cep', {
        cep: $('input[name="addr_cep"]').val(),
      }, function(data) {
        $("[id='addr_cidade']").val(data["cidade"]);
        $("[id='addr_uf']").val(data["uf"]);
        $("[id='addr_bairro']").val(data["bairro"]);
        $("[id='addr_rua']").val(data["rua"]);
        $("[id='addr_num']").val(data["num"]);
        $("[id='addr_compl']").val(data["compl"]);
      });
    }
  });
  var selected = $("select").attr('id');
  $("select").val(selected);
});
