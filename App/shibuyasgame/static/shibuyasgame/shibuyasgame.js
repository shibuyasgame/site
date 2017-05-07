
$(document).ready(function(){
  setInterval(updateTime, 1000);
  setInterval(syncTime, 60606);
  $('.equipper').click(function(){
    equip($(this).attr("value"));
  });
  $('.dequipper').click(function(){
    dequip($(this).attr("value"));
  });
  $('.consumer').click(function(){
    consume($(this).attr("value"), 1);
  });
  $('#slide').click(function(){
    var bar = $('.rightbar');
    var rc = $('#rightcontainer');
    var h = bar.height();
    if(rc.is(":hidden")){
      this.innerHTML = "▼";
      h = getHeight(rc);
    }
    else {
      this.innerHTML ="▲";
    }
    rc.slideToggle(h);
    /*
    if(bar.width() > 50)
    {
      bar.animate({'width':'40px'}, 'slow');
      this.innerHTML = "<<";
      rc.hide();
    }
    else{
      this.innerHTML = ">>";
      rc.show();
      bar.animate({'width': '400px'}, 'slow');
      $('#summon').attr('id', 'dismiss');
    } */
  });
  /*
  $('').click(function)
  {
    if(rc.html().indexOf("main_food") != -1)
    {
      $('#rightcontainer').html($('#main_food_template').html());
    }
  } */
})



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

// Timer
function updateTime(){
  var datetime = document.getElementById("time").innerHTML.split("<br>");
  var date = datetime[0].split('-');
  var time = datetime[1].split(":");
  var carry = false;
  var sec = parseInt(time[2]); var min = parseInt(time[1]); var hour = parseInt(time[0]);
  var year = parseInt(date[0]); var mon = parseInt(date[1]);; var day = parseInt(date[2]);
  var ans = "Y-MON-D<br>H:MIN:S";
  if(sec < 59) // Seconds
    ans = ans.replace("S", zeropad(sec+1));
  else {
    ans = ans.replace("S", "00");
    carry = true;
  }
  if(carry) // Minutes
  {
    carry = false;
    if(min < 59)
      ans = ans.replace("MIN", zeropad(min+1));
    else{
      ans = ans.replace("MIN", "00");
      carry = true;
    }
  }
  if(carry) // Hours
  {
    carry = false;
    if(hour < 24)
      ans = ans.replace("H", zeropad(hour+1));
    else{
      ans = ans.replace("H", "00");
      carry = true;
    }
  }
  if(carry) // Day
  {
    carry = false;
    if(day < daysInMonth(mon, year))
      ans = ans.replace("D", zeropad(day+1));
    else{
      ans = ans.replace("D", "01");
      carry = true;
    }
  }
  if(carry) // Month
  {
    carry = false;
    if(mon < 12)
      ans = ans.replace("MON", zeropad(mon+1));
    else{
      ans = ans.replace("MON", "01");
      carry = true;
    }
  }
  if(carry) // Year
  {
    ans = ans.replace("Y", (year+1).toString());
  }
  ans = ans.replace("Y", year);
  ans = ans.replace("MON", zeropad(mon));
  ans = ans.replace("D", zeropad(day));
  ans = ans.replace("H", zeropad(hour));
  ans = ans.replace("MIN", zeropad(min));
  document.getElementById("time").innerHTML = ans;
}
function zeropad(val){
  if(val.toString().length < 2)
    return "0" + val.toString();
  return val.toString();
}
function daysInMonth(month, year){
  if(month == 2)
  {
    if(year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)){return 29;}
    return 28;
  }
  if(month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)
      return 31;
  return 30;
}

function syncTime(){
  $.ajax({
    url: "/serverTime",
    type:"GET",
    dataType:'json',
    success: function(data){
      $("#time").html(data);
    },
    error: function(){
      // Don't do anything
    }
  });
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
