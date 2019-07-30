$(function() {
  $("#addr_cep_nat").on('input', function() {
    if ($(this).val().length == 8) {
      $.getJSON($SCRIPT_ROOT + '/cep', {
        cep: $('input[name="addr_cep_nat"]').val(),
      }, function(data) {
        $("[id='addr_city']").val(data["cidade"]);
        $("[id='addr_uf']").val(data["uf"]);
        $("[id='addr_bairro']").val(data["bairro"]);
        $("[id='addr_rua']").val(data["rua"]);
        $("[id='addr_num']").val(data["num"]);
        $("[id='addr_compl']").val(data["compl"]);
      });
    }
  });
});
$(function() {
  $("#addr_cep_leg").on('input', function() {
    if ($(this).val().length == 8) {
      $.getJSON($SCRIPT_ROOT + '/cep', {
        cep: $('input[name="addr_cep_leg"]').val(),
      }, function(data) {
        $("[id='addr_city']").val(data["cidade"]);
        $("[id='addr_uf']").val(data["uf"]);
        $("[id='addr_bairro']").val(data["bairro"]);
        $("[id='addr_rua']").val(data["rua"]);
        $("[id='addr_num']").val(data["num"]);
        $("[id='addr_compl']").val(data["compl"]);
      });
    }
  });
});
