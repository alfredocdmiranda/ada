var build_box_title = function(title){
  var box_title = document.createElement("h3");
  box_title.setAttribute("class", "box-title");
  box_title.innerHTML = title

  return box_title
}

var build_box_collapse = function(){
  var div_collapse = document.createElement("div");
  div_collapse.setAttribute("class", "box-tools pull-right");

  var btn_collapse = document.createElement("button");
  btn_collapse.setAttribute("class", "btn btn-box-tool");
  btn_collapse.setAttribute("data-widget", "collapse");
  div_collapse.appendChild(btn_collapse);
  var i_collapse = document.createElement("i");
  i_collapse.setAttribute("class", "fa fa-minus");
  btn_collapse.appendChild(i_collapse);

  return div_collapse;
}

var build_box_header = function(title){
  var box_header = document.createElement("div");
  box_header.setAttribute("class", "box-header with-border");

  box_title = build_box_title(title);
  box_header.appendChild(box_title);
  box_collapse = build_box_collapse();
  box_header.appendChild(box_collapse);

  return box_header;
}

var build_box_body = function(node){
  var box_body = document.createElement("div");
  box_body.setAttribute("class", "box-body no-padding");

  var box_body_row = document.createElement("div");
  box_body_row.setAttribute("class", "row");
  box_body.appendChild(box_body_row);
  var box_body_row_col = document.createElement("div");
  box_body_row_col.setAttribute("class", "col-md-12 col-sm-9");
  box_body_row.appendChild(box_body_row_col);

  //for(index_sensors=0;index_sensors < node['sensors'].length;index_sensors++){
  for(var key in node['sensors']){
    smallbox = build_smallbox(node['sensors'][key], node['id']);
    box_body_row_col.appendChild(smallbox);
  }

  smallbox = smallbox_battery(node);
  box_body_row_col.appendChild(smallbox);

  return box_body;
}

var build_smallbox = function(sensor, node_id){
  var smallbox = smallbox_funcs[sensor['type']](sensor, node_id);

  return smallbox;
}

var build_box = function(node){
  var main_row = document.getElementById('main-row');
  var column = document.createElement("div");
  column.setAttribute("class", "col-md-2");
  main_row.appendChild(column);
  var box = document.createElement("div");
  box.setAttribute("class", "box");
  column.appendChild(box);
  box_header = build_box_header(node['sketch_name']);
  box.appendChild(box_header);
  box_body = build_box_body(node);
  box.appendChild(box_body);
}

var build_dashboard = function(data){
  var nodes = data
  for(index_nodes=0; index_nodes < nodes.length; index_nodes++){
    build_box(nodes[index_nodes])
  }
}

var smallbox_light_switch = function(sensor, node_id){
  var smallbox = document.createElement("div");
  smallbox.setAttribute("class", "small-box bg-gray");

  var smallbox_inner = document.createElement("div");
  smallbox_inner.setAttribute("class", "inner");
  smallbox.appendChild(smallbox_inner);
  var smallbox_info = document.createElement("h3");
  smallbox_inner.appendChild(smallbox_info);

  var light_switch = document.createElement("input");
  light_switch.setAttribute("type", "checkbox");
  light_switch.setAttribute("name", "my-checkbox");
  console.log("SENSOR")
  console.log(sensor)
  if(sensor['values']['2'] == 1){
    light_switch.setAttribute("checked", "");
  }
  light_switch.setAttribute("data-node-id", node_id);
  light_switch.setAttribute("data-sensor-id", sensor['id']);
  light_switch.setAttribute("data-variable", "2");
  smallbox_info.appendChild(light_switch);

  var smallbox_title = document.createElement("p");
  smallbox_title.innerHTML = sensor['description'];
  smallbox_inner.appendChild(smallbox_title);
  var smallbox_icon = document.createElement("div");
  smallbox_icon.setAttribute("class", "icon");
  smallbox.appendChild(smallbox_icon);
  var smallbox_icon_i = document.createElement("i");
  smallbox_icon_i.setAttribute("class", "ion ion-lightbulb");
  smallbox_icon.appendChild(smallbox_icon_i);

  return smallbox;
}

var smallbox_temperature = function(sensor, node_id){
  var smallbox = document.createElement("div");
  if(sensor['values'][0] < 25){
    color = 'bg-blue';
  }else if(sensor['values'][0] >= 25 && sensor['values'][0] < 30){
    color = 'bg-orange';
  }else{
    color = 'bg-red';
  }

  smallbox.setAttribute("class", "small-box "+color);
  var smallbox_inner = document.createElement("div");
  smallbox_inner.setAttribute("class", "inner");
  smallbox.appendChild(smallbox_inner);
  var smallbox_info = document.createElement("h3");
  smallbox_info.innerHTML = sensor['values'][0]+"°C";
  smallbox_inner.appendChild(smallbox_info);
  var smallbox_title = document.createElement("p");
  smallbox_title.innerHTML = sensor['description'];
  smallbox_inner.appendChild(smallbox_title);
  var smallbox_icon = document.createElement("div");
  smallbox_icon.setAttribute("class", "icon");
  smallbox.appendChild(smallbox_icon);
  var smallbox_icon_i = document.createElement("i");
  smallbox_icon_i.setAttribute("class", "ion ion-thermometer");
  smallbox_icon.appendChild(smallbox_icon_i);

  return smallbox;
}

var smallbox_battery = function(node){
  var smallbox = document.createElement("div");
  if(node['battery_level'] < 25){
    color = 'bg-red';
    icon = 'low';
  }else if(node['battery_level'] >= 25 && node['battery_level'] < 50){
    color = 'bg-orange';  console.log(nodes)
    icon = 'half';
  }else{
    color = 'bg-green';
    icon = 'full';
  }

  smallbox.setAttribute("class", "small-box "+color);
  var smallbox_inner = document.createElement("div");
  smallbox_inner.setAttribute("class", "inner");
  smallbox.appendChild(smallbox_inner);
  var smallbox_info = document.createElement("h3");
  smallbox_info.innerHTML = node['battery_level']+"%";
  smallbox_inner.appendChild(smallbox_info);
  var smallbox_title = document.createElement("p");
  smallbox_title.innerHTML = "Battery Level";
  smallbox_inner.appendChild(smallbox_title);
  var smallbox_icon = document.createElement("div");
  smallbox_icon.setAttribute("class", "icon");
  smallbox.appendChild(smallbox_icon);
  var smallbox_icon_i = document.createElement("i");
  smallbox_icon_i.setAttribute("class", "ion ion-battery-"+icon);
  smallbox_icon.appendChild(smallbox_icon_i);

  return smallbox;
}

var smallbox_funcs = {
  3: smallbox_light_switch,
  6: smallbox_temperature
}

var load_bootstrapSwitch = function(csrf_token){
  $("[name='my-checkbox']").bootstrapSwitch();
  $('[name="my-checkbox"]').on('switchChange.bootstrapSwitch', function(event, state) {
    node_id = this.getAttribute("data-node-id");
    sensor_id = this.getAttribute("data-sensor-id");
    variable = this.getAttribute("data-variable");
    value = state ? 1 : 0;

    var ajaxReq = $.ajax({
                method: "PUT",
                //dataType: 'json',
                url: "/api/nodes/"+node_id+"/sensors/"+sensor_id,
                data: {"variable": variable, "value": value},

                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    }
                }
              });
    ajaxReq.done(function(msg){
              console.log(msg);
            });
    ajaxReq.fail(function(msg){
              alert( "Fail: " + msg);
              console.log(msg);
            });
    });
}
