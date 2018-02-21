var remote = require('electron').remote;
var ipcRenderer = require('electron').ipcRenderer;

var smartthingsTokenValue = null;
var pageNum = 10;

var onhubUUID = [];
var packetUUID = [];
var alexaUUID = null;
var smartThingsUUID = null;

$("body").on("keyup", "form", function(e){
  if (e.which == 13){
    if ($(".btn").is(":visible") && $("fieldset.current").find("input, textarea").valid() ){
      e.preventDefault();
      nextSection();
      return false;
    }
  }
});
 
 
$(".btn").on("click", function(e){

  pageNum = nextSection();

  if(pageNum == 0) {
    SmartThingsPage();
  }
  else if(pageNum == 1) {
    AlexaPage();
  }
  else if(pageNum == 2) {
    ResultPage();
  }

});
 
$("form").on("submit", function(e){
  if ($(".btn").is(":visible") || $("fieldset.current").index() < 3){
    e.preventDefault();
  }
});
 
function goToSection(i){
  $("fieldset:gt("+i+")").removeClass("current").addClass("next");
  $("fieldset:lt("+i+")").removeClass("current");
  $("li").eq(i).addClass("current").siblings().removeClass("current");
  setTimeout(function(){
    $("fieldset").eq(i).removeClass("next").addClass("current active");
      if ($("fieldset.current").index() == 3){
        $(".btn").hide();
        $("input[type=submit]").show();
      } else {
        //$(".btn").show();
        $("input[type=submit]").hide();
      }
  }, 80);
}
 
function nextSection(){
  var i = $("fieldset.current").index();
  if (i < 3){
    $("li").eq(i+1).addClass("active");
    goToSection(i+1);
    return i;
  }
}

$("li").on("click", function(e){
  var i = $(this).index();
  if ($(this).hasClass("active")){

  } else {
    alert("Please complete previous sections first.");
  }
});

function ResultPage() {

  var checkOnhub = false;
  var checkPacket = false;
  var ckeckSmartThings = false;

  var onHubLength = onhubUUID.length;
  var packetLength = packetUUID.length;

  var onHubFlag = setInterval(function() {
    if(onHubLength == 0) {
      checkOnhub = 'true';
      clearInterval(onHubFlag);
    }
    else {
      for (var index = 0; index < onHubLength; index++) {
        $.getJSON('http://127.0.0.1:31337/task/status/' + onhubUUID[index][1], function( data ) {
          if(data['status'] == 'success') {
            delete onhubUUID[index];
            onHubLength -= 1;
            if(onHubLength == 0) {
              checkOnhub = 'true';
              clearInterval(onHubFlag);
            }
          }
        });
      }
    }
  }, 3000);

  var packetFlag = setInterval(function() {
    if(packetLength == 0) {
      checkPacket = 'true';
      clearInterval(packetFlag);
    }
    else {
      for (var index = 0; index < packetLength; index++) {
        $.getJSON('http://127.0.0.1:31337/task/status/' + packetUUID[index][1], function( data ) {
          if(data['status'] == 'success') {
            delete packetUUID[index];
            packetLength -= 1;
            if(packetLength == 0) {
              checkPacket = 'true';
              clearInterval(packetFlag);
            }
          }
        });
      }
    }
  }, 3000);

  var smartthingsFlag = setInterval(function() {
    if(smartThingsUUID == null) {
      ckeckSmartThings = 'true';
          clearInterval(smartthingsFlag);
    }
    else {
      $.getJSON('http://127.0.0.1:31337/task/status/' + smartThingsUUID, function( data ) {
        if(data['status'] == 'success') {
          ckeckSmartThings = 'true';
          clearInterval(smartthingsFlag);
        }
      });
    }
  }, 3000);

  
  var finalFlag = setInterval(function() {
    if(checkOnhub == 'true' && ckeckSmartThings == 'true' && ckeckSmartThings == 'true') {
      $(".loading-final").hide();
      $(".text-final").show();
      $(".final-button").show();
      clearInterval(finalFlag);
    }
  }, 1000);

  $(".final-button").on( "click", function() {
    ipcRenderer.send('start-parsing', 1);
    setTimeout(function() {
      window.location.replace("networkMap.html");
    }, 3000);
  });

}

function AlexaPage() {

  $(".btn-smartthings").fadeOut();

  var alexaRadioButton = null;

  $( ".alexa-radio" ).on( "click", function() {
    collectRadioButton = $( ".alexa-radio:checked" ).val();

    if(collectRadioButton == 'yes'){
      $(".btn-amazon-echo").hide();
      $(".check-amazon-echo-data").show();
    }
    else {
      $(".check-amazon-echo-data").hide();
      $(".btn-amazon-echo").show();
    }

  });

  $(".check-amazon-echo-data").on( "click", function() {

    var alexaData = { 'service' : 'alexa' };

    $.post('http://127.0.0.1:31337/task/request/account', alexaData, function(response) {
      alexaUUID = response['task_id'];
        var alexaFlag = setInterval(function() {

          $.getJSON('http://127.0.0.1:31337/task/status/' + alexaUUID, function( data ) {

            if(data['status'] == 'success') {
              $(".check-amazon-echo-data").hide();
              $(".btn-amazon-echo").show();
              clearInterval(playAlert);
            }

          }, 'json').fail(function() {
            alert( "Error. Please click one more." );
          });

        }, 3000);
      });
  });

  $(".btn-amazon-echo").on( "click", function() {
    $(".btn-amazon-echo").hide();
  });
}

function SmartThingsPage() {

  var collectRadioButton = null;

  $(".btn-smartthings").fadeOut();

  $( ".smartthings-radio" ).on( "click", function() {
    collectRadioButton = $( ".smartthings-radio:checked" ).val();

    if(collectRadioButton == 'yes'){
      $("#smartthings-token-input").fadeIn();
      $(".btn-smartthings").hide();
      if(smartthingsTokenValue == '') {
        $(".btn-smartthings").hide();
      }
    }
    else {
      $("#smartthings-token-input").fadeOut();
      $(".check-token-available").hide();
      $(".btn-smartthings").show();
    }

  });

  $(".check-token-available").on( "click", function() {
    checkSmartThingsToken(smartthingsTokenValue);
  });

  $("#smartthings-token-input").keyup(function() {
    smartthingsTokenValue = $( this ).val();
    // if Token length is more then 10, button is available
    if(smartthingsTokenValue.length == 36) {
      $(".check-token-available").show();
    } 
    else {
      $(".check-token-available").hide();
    }
  }).keyup();
}

function checkSmartThingsToken(token) {

  token_data = {'service' : 'smartthings', 'access_token' : token};

  $.post('http://127.0.0.1:31337/task/request/account', token_data, function(response) {
    smartThingsUUID = response['task_id'];

    $.getJSON('http://127.0.0.1:31337/task/status/' + smartThingsUUID, function( data ) {
      if(data['status'] != 'failure') {
        $(".btn-smartthings").click();
        $(".check-token-available").hide();
      }
      else {
        alert( "The token value is not valid." );
      }
    }, 'json').fail(function() {
      alert( "error." );
    });

  }, 'json').fail(function() {
    alert( "error" );
  });
}

function basicInfoPage() {

  var timeZone = null;
  var inputDirName = null;

  // Fake Button for directory button
  document.getElementById('getDirInput').addEventListener('click', _ => {
    document.getElementById('SearchDirButton').click();
  })

  // Get directory
  $('#SearchDirButton').change(function() { 
    inputDirName = this.files[0].path;
    $("#getDirInput").attr('placeholder',inputDirName);
    if(inputDirName != null) {
      $(".check-basic-info").show();
    }
  });

  // Setting Timezone
  $('#getTimeZone').timezonePicker({
      quickLink: [{

      }],
      showHoverText : false,
      hoverColor : '#5a8cbc'
  });
  $('#getTimeZone select').val('Asia/Seoul');

  // 다음 버튼 누르면서 값 획득
  $(".check-basic-info").click(function(){
    timeZone = $('#getTimeZone select').val();
    sendTimezone(timeZone);
    sendDir(inputDirName);
    $(".check-basic-info").hide();
    $(".basic-info-loading").show();

  });
}

function sendTimezone(timeZone) {
  remote.getGlobal('sharedObj').timezone = timeZone;
  ipcRenderer.send('get-timezone');
}

function sendDir(inputDirName) {

  data = { 'filepath' : inputDirName };

  $.post('http://127.0.0.1:31337/task/bulk', data, function(response) {
    for(var temp in response) {
      if (response[temp]['filetype'] == 'onhub') {
        onhubUUID.push([temp, response[temp]['task_id']]);
      }
      else if(response[temp]['filetype'] == 'packet') {
        packetUUID.push([temp, response[temp]['task_id']]);
      }
    }
    $(".basic-info-loading").hide();
    $(".btn-basic-info").click();
  }, 'json').fail(function() {
    alert( "error" );
    $(".basic-info-loading").hide();
    $(".check-basic-info").show();
  });

}

basicInfoPage();