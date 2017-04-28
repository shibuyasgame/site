// TOGGLE
$(function () {
  $('.toggle-heading').on('click', function() {
    var toslide = $(this).next('.toggle-content');
    var h = toslide.height();
    if(toslide.is(":hidden")){
      h = getHeight(toslide);
    }
    toslide.slideToggle(h);
  });
});

// GETHEIGHT
function getHeight(item){
  var previousCss = $(item).attr("style");
  $(item)
      .css({
          position:   'absolute',
          visibility: 'hidden',
          display:    'block'
      });
  var h = $(item).height();
  $(item).attr("style", previousCss ? previousCss : "");
  return h;
}


function toast(t, text, time) {
  $(t).text(text).fadeIn(200).delay(time).fadeOut(200);
}
function toastin(text){
  $('.toast').text(text).fadeIn(200);
}
// Taken from ajax-example
function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

$(document).ready(function(){
  $('.equipper').click(function(){
    equip($(this).attr("value"));
    console.log($(this).attr("value"));
  });
  $('.dequipper').click(function(){
    dequip($(this).attr("value"));
  });
  $('.consumer').click(function(){
    consume($(this).attr("value"), 1);
  });
})

function equip(item_id){
  $.ajax({
    url: "/equip/"+$('#charname').html()+ $('#suffix').html() +"/"+item_id,
    type:"POST",
    data:{'csrfmiddlewaretoken': getCSRFToken()},
    dataType:'json',
    success: function(){
      updateInventory();
    },
    error: function(){
      errorMessage("You can't do that.");
    }
  });
}

function dequip(item_id){
  $.ajax({
    url: "/dequip/"+$('#charname').html()+ $('#suffix').html() +"/"+item_id,
    type:"POST",
    data:{'csrfmiddlewaretoken': getCSRFToken()},
    dataType:'json',
    success: function(){
      updateInventory();
    },
    error: function(){
      errorMessage("You can't do that.");
    }
  });
}

function consume(item_id, quantity){
  $.ajax({
    url: "/consume/"+$('#charname').html()+ $('#suffix').html() +"/"+item_id+"/"+quantity,
    type:"POST",
    data:{'csrfmiddlewaretoken': getCSRFToken()},
    dataType:'json',
    success: function(){
      updateInventory();
    },
    error: function(){
      errorMessage("You can't do that.");
    }
  });
}

function updateInventory()
{
  location.reload();
}

function errorMessage(message)
{
  $('#errorcorner').html(message);
}
