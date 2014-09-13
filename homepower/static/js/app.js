$(function(){

  var socket = io.connect();
  var set_data = function(data) {
    $("#now_power_value").html(data["watt"].toFixed(2));
    $("#now_power_time").html(data["date"]);
  }

  $.ajax({
    type: "GET",
    url: "/api/watt/latest",
    dataType: "json",
    cache: false,
    success: function(data, dataType) {
      set_data(data);
    }
  });

  socket.on("connect", function(){
    console.log("connected");

    socket.emit("subscribe");

    socket.on("tick", function(data){
      console.log(data);
      set_data(data);
    });
  });

});


$(function(){

  var set_data = function(data) {
    var kilo_watt = data["watt"] / 1000;
    $("#today_power_value").html(kilo_watt.toFixed(2));
    var charge = kilo_watt * 19.43;
    $("#today_power_charge").html(charge.toFixed(2));
    console.log(data);
  }

  var load_data = function() {
    $.ajax({
      type: "GET",
      url: "/api/watt/today",
      dataType: "json",
      cache: false,
      success: function(data, dataType) {
        set_data(data);
      }
    });
  }

  load_data();
  setInterval(load_data, 1000 * 60 * 10);
});


$(function(){

  var set_data = function(data) {
    var kilo_watt = data["watt"] / 1000;
    $("#month_power_value").html(kilo_watt.toFixed(2));
    var charge = kilo_watt * 19.43;
    $("#month_power_charge").html(charge.toFixed(2));
    console.log(data);
  }

  var load_data = function() {
    $.ajax({
      type: "GET",
      url: "/api/watt/month",
      dataType: "json",
      cache: false,
      success: function(data, dataType) {
        set_data(data);
      }
    });
  }

  load_data();
  setInterval(load_data, 1000 * 60 * 10);
});
