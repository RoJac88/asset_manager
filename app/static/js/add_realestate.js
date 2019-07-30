$(function() {

  $(".owner_id").on('input', function() {
    if ($(this).val().length >= 11) {
      var index = parseInt(this.id.split("-")[1], 10);
      $.getJSON($SCRIPT_ROOT + '/_get_person', {
        id: $(this).val(),
      }, function(data) {
        $('#info-'+index).val(data["name"]);
      });
    }
  });

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

  $("#add_own").on('click', function() {
    var $newOwner = $('.owner_form').last().clone();
    $newOwner.find("input[type='text']").val("");
    var tags = $newOwner.children().prop("for").split("-");
    var index = parseInt(tags[1], 10);
    var next = index + 1;
    if (($newOwner).find(".btn-danger").length == 0) {
      var $inner = $("<span/>", {"class": "glyphicon glyphicon-trash"});
      var $outter = $("<button/>", {"class": "btn btn-danger btn-sm form-control", "id": next});
      $newOwner.append($outter.append($inner.append()))
    } else {
      $newOwner.find(".btn-danger").last().attr({id: next});
    };
    var ownerTag = "owners-"+index+"-owner";
    var shareTag = "owners-"+index+"-share";
    var ownerTagNext = "owners-"+next+"-owner";
    var shareTagNext = "owners-"+next+"-share";
    $($newOwner).find(".owner_id_label").last().attr("for", ownerTagNext);
    $($newOwner).find(".owner_id").last().attr({
      id: ownerTagNext,
      name: ownerTagNext,
      }).on('input', function() {
        if ($(this).val().length >= 11) {
          var index = parseInt(this.id.split("-")[1], 10);
          $.getJSON($SCRIPT_ROOT + '/_get_person', {
            id: $(this).val(),
          }, function(data) {
            $('#info-'+index).val(data["name"]);
          });
        }
      });
    $($newOwner).find(".owner_share_label").last().attr("for", shareTagNext);
    $($newOwner).find(".owner_share").last().attr({
      id: shareTagNext,
      name: shareTagNext,
      });
    $($newOwner).find(".btn-danger").last().on('click', function() {
      $(this).parent().remove();
      $('#info-'+this.id).remove();
      });
    $newOwner.appendTo("#estate_owners");
    $("#estate_owners").find("div").last().addClass("owner_id-"+next);
    var $info = $("<input id=info-"+next+" class='form-control owner-info' style='height:39px' type='text' value='' disabled>");
    var $divInfo = $('<div/>', {
      "class": 'form-group from-inline owner-info-'+next,
    });
    $($info).appendTo($divInfo)
    $divInfo.appendTo("#owners_info")
    });
  });
