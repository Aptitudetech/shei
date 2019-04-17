// Copyright (c) 2019, Aptitude technologie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Configurator', {
	onload: function(frm){
		if (frappe.user.has_role("System Manager")){
			var item_discount = frappe.meta.get_docfield("Price Configurator Item", "item_discount_pourcent", cur_frm.doc.name);
			item_discount.read_only = 0;
			var price_line = frappe.meta.get_docfield("Price Configurator Item", "price_line", cur_frm.doc.name);
			price_line.read_only = 0;	
		}
	},
	refresh: function(frm) {
	},
	test: function(frm) {
		frappe.call({
				method: "test",
				doc: frm.doc,
				args: {
				},
		callback: function(content) {
			var iframe = document.createElement('iframe');
			var html = content.message;
			iframe.src = 'data:text/html;charset=utf-8,' + encodeURI(html);
			document.body.appendChild(iframe);
			console.log('iframe.contentWindow =', iframe.contentWindow);
			console.log(content.message)
			//window.open("www.packit4me.com/api/call/preview", '_blank',content);
			//newWindow.document.body.innerHTML = content.message;

			var f = '  dsf <  df >'
			var newWindow = window.open();
			newWindow.document.body.innerHTML = `
			<!DOCTYPE html>
            <html lang="en">
            <head>
        <title>preview</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
        <style>
            body {
                color: #000;
                font-family:Monospace;
                font-size:13px;
                text-align:center;
                font-weight: bold;

                background-color: #fff;
                margin: 0px;
                overflow: hidden;
            }

            #info {
                color:#000;
                position: absolute;
                top: 0px; width: 100%;
                padding: 5px;

            }

            a {
                color: red;
            }
        </style>
    <style type="text/css">
@font-face {
  font-weight: 400;
  font-style:  normal;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-Regular.woff2') format('woff2');
}
@font-face {
  font-weight: 400;
  font-style:  italic;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-Italic.woff2') format('woff2');
}

@font-face {
  font-weight: 500;
  font-style:  normal;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-Medium.woff2') format('woff2');
}
@font-face {
  font-weight: 500;
  font-style:  italic;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-MediumItalic.woff2') format('woff2');
}

@font-face {
  font-weight: 700;
  font-style:  normal;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-Bold.woff2') format('woff2');
}
@font-face {
  font-weight: 700;
  font-style:  italic;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-BoldItalic.woff2') format('woff2');
}

@font-face {
  font-weight: 900;
  font-style:  normal;
  font-family: 'Inter-Loom';

  src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-Black.woff2') format('woff2');
}
@font-face {
  font-weight: 900;
  font-style:  italic;
  font-family: 'Inter-Loom';
  </style>
  <style>src: url('https://cdn.useloom.com/assets/fonts/inter/Inter-UI-BlackItalic.woff2') format('woff2');</style>
        <style type="text/css">tcxspan{text-decoration: underline; cursor: pointer;}</style>


        <script type="text/javascript" src="js/three.js"></script>
        <script type="text/javascript" src="js/TrackballControls.js"></script>
        <script type="text/javascript" src="js/Detector.js"></script>
        <script>
          var packedBins = JSON.parse("[{\"size\": \"5 x 5 x 5\",\"id\": \"0\",\"size_1\": 5,\"size_2\": 5,\"size_3\": 5,\"weight_limit\": 50,\"curr_weight\": 15,\"item_count\": 2,\"items\": [{\"id\": \"1\",\"orig_size\": \"2 x 4 x 2\",\"sp_size\": \"2 x 4 x 2\",\"size_1\": 2,\"size_2\": 4,\"size_3\": 2,\"sp_size_1\": 2,\"sp_size_2\": 4,\"sp_size_3\": 2,\"x_origin_in_bin\": -1.5,\"y_origin_in_bin\": -0.5,\"z_origin_in_bin\": 1.5,\"weight\": 10,\"constraints\": 0},{\"id\": \"0\",\"orig_size\": \"1 x 2 x 3\",\"sp_size\": \"1 x 2 x 3\",\"size_1\": 1,\"size_2\": 2,\"size_3\": 3,\"sp_size_1\": 1,\"sp_size_2\": 2,\"sp_size_3\": 3,\"x_origin_in_bin\": 0,\"y_origin_in_bin\": -1.5,\"z_origin_in_bin\": 1,\"weight\": 5,\"constraints\": 0}]}]");
          var binIdToRender = "0";
          if ( ! Detector.webgl ) Detector.addGetWebGLMessage();
          var container;
          var camera, controls, scene, renderer;
          var cross;
          var randomColorsUsedAlready = new Object();
          var itemColorHash = new Object();
          var itemType = "normal";  
          function onLoadBody (){
              init();
              animate();
          } 


          function init() {
              var bin = null;
              for(var i=0; i < packedBins.length; i++) {
                  if( packedBins[i].id == binIdToRender) {
                      bin = packedBins[i];
                  }
              }                          
              if( bin == null) {
                  alert("Error.  Could not find bin");
                  return;
              }
              if( bin.size_3 == undefined)
                  bin.size_3 = 0.25;

              camera = new THREE.PerspectiveCamera( 60, window.innerWidth / window.innerHeight, 1, 1000 );
              camera.position.x = (bin.size_1 + bin.size_2 + bin.size_3 ) * .25;
              camera.position.y = (bin.size_1 + bin.size_2 + bin.size_3 ) * .25;
              camera.position.z = (bin.size_1 + bin.size_2 + bin.size_3 ) * .5;
              controls = new THREE.TrackballControls( camera );
              controls.rotateSpeed = 1.0;
              controls.zoomSpeed = 1.2;
              controls.panSpeed = 0.8;
              controls.noZoom = false;
              controls.noPan = false;
              controls.staticMoving = true;
              controls.dynamicDampingFactor = 0.3;
              controls.keys = [ 65, 83, 68 ];
              controls.addEventListener( 'change', render );

              // world

              scene = new THREE.Scene();
              scene.fog = new THREE.FogExp2( 0x000000, 0.002 );
              var binGeometry = new THREE.CubeGeometry( bin.size_1,bin.size_2,bin.size_3 );
              var binMaterial =  new THREE.MeshPhongMaterial( { color:0xffffff, shading: THREE.SmoothShading, wireframe: true } );
              var binMesh = new THREE.Mesh( binGeometry, binMaterial );
              binMesh.position.x = 0;
              binMesh.position.y = 0;
              binMesh.position.z = 0;
              binMesh.updateMatrix();
              binMesh.matrixAutoUpdate = false;
              scene.add( binMesh );
              for(var i=0; i < bin.items.length; ++i) {
                  drawItems( scene, bin.items[i]);
              }

              // lights

              ambientLight = new THREE.AmbientLight( 0x444444 );
              scene.add( ambientLight );
              pointLight = new THREE.PointLight( 0xffffff, 1.25, 1000 );
              pointLight.position.set( 0, 0, 600 );
              scene.add( pointLight );
              directionalLight = new THREE.DirectionalLight( 0xffffff );
              directionalLight.position.set( 1, -0.5, -1 );
              scene.add( directionalLight );

              // renderer
              renderer = new THREE.WebGLRenderer( { antialias: false } );
              renderer.setClearColor( scene.fog.color, 1 );
              renderer.setSize( window.innerWidth, window.innerHeight );
              container = document.getElementById( 'container' );
              container.innerHTML = "";
              container.appendChild( renderer.domElement );
              createLegend(container);
              window.addEventListener( 'resize', onWindowResize, false );
          }

          function drawItems(scene, item) {

              var is3sided = true;
              if( item.sp_size_3 == undefined) {
                  item.sp_size_3 = 0.25;
                  is3sided = false;
              }
              var itemGeometry = new THREE.CubeGeometry( item.sp_size_1, item.sp_size_2, item.sp_size_3 );
              var color = randomColor();
              itemColorHash[item.id + " : " + item.sp_size] = color;
              var itemMaterial;
              if( itemType == "normal")
                  itemMaterial =  new THREE.MeshPhongMaterial( { color:color, shading: THREE.SmoothShading } );
              else if ( itemType == "wireframe" )
                  itemMaterial =  new THREE.MeshPhongMaterial( { color:color, shading: THREE.SmoothShading, wireframe: true } );
              else if ( itemType == "transparent")
                  itemMaterial =  new THREE.MeshPhongMaterial( { color:color, shading: THREE.SmoothShading,transparent: true, opacity: 0.8 } );    
              itemMaterial.name = item.id;
              var itemMesh = new THREE.Mesh( itemGeometry, itemMaterial );
              itemMesh.position.x = item.x_origin_in_bin;
              itemMesh.position.y = item.y_origin_in_bin;
              if(is3sided)
                  itemMesh.position.z = item.z_origin_in_bin;
              itemMesh.updateMatrix();
              itemMesh.matrixAutoUpdate = false;
              scene.add( itemMesh );           
          }


          function randomColor(){
              var color = '#'+Math.floor(Math.random()*16777215).toString(16);
              if( randomColorsUsedAlready[color] == true)
                  randomColor();
              else
                  randomColorsUsedAlready[color] = true;
              return color;      
          }

          function createLegend(container) {
              var legend = document.createElement('div');
              var table = document.createElement('table');
              var headerrow = document.createElement('tr');
              var headercell = document.createElement('td');
              headercell.colSpan = 3;
              headercell.innerHTML = "contents legend";
              headerrow.appendChild(headercell);
              table.appendChild(headerrow);
              var hrrow = document.createElement('tr');
              var hrcell = document.createElement('td');
              hrcell.colSpan = 3;
              hrcell.appendChild(document.createElement('hr'));
              hrrow.appendChild(hrcell);
              table.appendChild(hrrow);
              legend.appendChild(table);

              for (var key in itemColorHash) {
                  if (itemColorHash.hasOwnProperty(key)) {
                      var row = document.createElement('tr');
                      var key_cell = document.createElement('td');
                      var sep_cell = document.createElement('td');
                      var color_cell = document.createElement('td');  
                      key_cell.innerHTML = key;
                      sep_cell.innerHTML = "=";
                      var color_div = document.createElement('span');
                      color_div.style.height = '10px'
                      color_div.style.width = '10px'
                      color_div.style.background = itemColorHash[key];
                      color_div.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                      color_cell.appendChild(color_div);
                      row.appendChild(key_cell);
                      row.appendChild(sep_cell);
                      row.appendChild(color_cell);
                      table.appendChild(row);
                  }
              }

              legend.style.position = 'absolute';
              legend.style.top = '100px';
              legend.style.color = "#ffffff";
              legend.style.fontSize = "12px";
              legend.style.zIndex = 100;
              container.appendChild( legend );
          }

          function onWindowResize() {
              camera.aspect = window.innerWidth / window.innerHeight;
              camera.updateProjectionMatrix();
              renderer.setSize( window.innerWidth, window.innerHeight );
              controls.handleResize();
              render();
          }

          function animate() {
              requestAnimationFrame( animate );
              controls.update();
          }

          function render() {
              renderer.render( scene, camera );
          }
      </script>
  </head>
    <body data-gr-c-s-loaded="true" onload="onLoadBody();">

        <button style="position: absolute; top: 0px; z-index: 100" onclick="itemType='normal'; init(); animate();">normal</button>
        <button style="position: absolute; top: 25px; z-index: 100" onclick="itemType='wireframe'; init(); animate();">wireframe</button>
        <button style="position: absolute; top: 50px; z-inde 100" onclick="itemType='transparent'; init(); animate();">transparent</button>
        <div id="container"><canvas width="1058" height="952"></canvas><div style="position: absolute; top: 100px; color: rgb(255, 255, 255); font-size: 12px; z-index: 100;"><table><tr><td colspan="3">contents legend</td></tr><tr><td colspan="3"><hr></td></tr><tr><td>1 : 2 x 4 x 2</td><td>=</td><td><span style="height: 10px; width: 10px; background: rgb(108, 0, 200);">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></td></tr><tr><td>0 : 1 x 2 x 3</td><td>=</td><td><span style="height: 10px; width: 10px; background: rgb(26, 104, 165);">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></td></tr></table></div></div>

    <loom-container id="lo-engage-ext-container"><loom-shadow classname="resolved"></loom-shadow></loom-container>

      </body>
      </html>
			`
			//newWindow.document.write(content.message);
			}
		});
	},
	calculate_final_price: function(frm) {
			if (frm.doc.__unsaved){
				frappe.throw(__("Please save the document before proceeding"));
			}
			frappe.call({
					method: "calculate_final_price",
					doc: frm.doc,
					args: {
					},
					freeze: true,
					freeze_message: "This operation may takes few minutes, please wait...",
			callback: function() {
				refresh_field("price_configurator_items");
					}
			});
	},
	pc_add_items: function(frm) {
		frappe.call({
				method: "pc_add_items",
				doc: frm.doc,
				args: {
					'default_items': cur_frm.doc.pc_default_items,
				},
				freeze: true,
				freeze_message: "This operation may takes few minutes, please wait...",
				callback: function() {
					refresh_field("price_configurator_items");
					refresh_field("pc_default_items");
				}
		});
	},
});


/*
<!DOCTYPE html>
			<html lang="en">
				<head>
					<title>preview</title>
					<meta charset="utf-8">
					<meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
					<style>
						body {
							color: #000;
							font-family:Monospace;
							font-size:13px;
							text-align:center;
							font-weight: bold;
			
							background-color: #fff;
							margin: 0px;
							overflow: hidden;
						}
			
						#info {
							color:#000;
							position: absolute;
							top: 0px; width: 100%;
							padding: 5px;
			
						}
			
						a {
							color: red;
						}
					</style>
				</head>
			
				<body>
				   
					<button style="position: absolute; top: 0px; z-index: 100" onclick="itemType=\'normal\'; init(); animate();">normal</button>
					<button style="position: absolute; top: 25px; z-index: 100" onclick="itemType=\'wireframe\'; init(); animate();">wireframe</button>
					<button style="position: absolute; top: 50px; z-index: 100" onclick="itemType=\'transparent\'; init(); animate();">transparent</button>
					<div id="container"></div>
			
			
					<script type="text/javascript" src="/resources/js/three.min.js"></script>
					<script type="text/javascript" src="/resources/js/TrackballControls.js"></script>
					<script type="text/javascript" src="/resources/js/Detector.js"></script>
					<script type="text/javascript" src="/resources/js/stats.min.js"></script>
			
					<script>
			
						var packedBins = JSON.parse("[{\"size\": \"10 x 10 x 10\",\"id\": \"0\",\"size_1\": 10,\"size_2\": 10,\"size_3\": 10,\"weight_limit\": 0,\"curr_weight\": 0,\"item_count\": 3,\"items\": [{\"id\": \"0\",\"orig_size\": \"3 x 3 x 3\",\"sp_size\": \"3 x 3 x 3\",\"size_1\": 3,\"size_2\": 3,\"size_3\": 3,\"sp_size_1\": 3,\"sp_size_2\": 3,\"sp_size_3\": 3,\"x_origin_in_bin\": -3.5,\"y_origin_in_bin\": -3.5,\"z_origin_in_bin\": 3.5,\"weight\": 0,\"constraints\": 0},{\"id\": \"0\",\"orig_size\": \"2 x 2 x 2\",\"sp_size\": \"2 x 2 x 2\",\"size_1\": 2,\"size_2\": 2,\"size_3\": 2,\"sp_size_1\": 2,\"sp_size_2\": 2,\"sp_size_3\": 2,\"x_origin_in_bin\": -1,\"y_origin_in_bin\": -4,\"z_origin_in_bin\": 4,\"weight\": 0,\"constraints\": 0},{\"id\": \"0\",\"orig_size\": \"1 x 1 x 1\",\"sp_size\": \"1 x 1 x 1\",\"size_1\": 1,\"size_2\": 1,\"size_3\": 1,\"sp_size_1\": 1,\"sp_size_2\": 1,\"sp_size_3\": 1,\"x_origin_in_bin\": -4.5,\"y_origin_in_bin\": -1.5,\"z_origin_in_bin\": 4.5,\"weight\": 0,\"constraints\": 0}]}]");
						var binIdToRender = "0";
					   
									
						if ( ! Detector.webgl ) Detector.addGetWebGLMessage();
			
						var container, stats;
			
						var camera, controls, scene, renderer;
			
						var cross;
						
						var randomColorsUsedAlready = new Object();
						var itemColorHash = new Object();
						
						var itemType = "normal";
											
											
						init();
						animate();
						
						function init() {
										
										
							var bin = null;
							for(var i=0; i < packedBins.length; i++) {
								if( packedBins[i].id == binIdToRender) {
									bin = packedBins[i];
								}
							}
							
															
							if( bin == null) {
								alert("Error.  Could not find bin");
								return;
							}
							
							if( bin.size_3 == undefined)
								bin.size_3 = 0.25;
						   
							camera = new THREE.PerspectiveCamera( 60, window.innerWidth / window.innerHeight, 1, 1000 );
							camera.position.x = (bin.size_1 + bin.size_2 + bin.size_3 ) * .25;
							camera.position.y = (bin.size_1 + bin.size_2 + bin.size_3 ) * .25;
							camera.position.z = (bin.size_1 + bin.size_2 + bin.size_3 ) * .5;
			
							controls = new THREE.TrackballControls( camera );
			
							controls.rotateSpeed = 1.0;
							controls.zoomSpeed = 1.2;
							controls.panSpeed = 0.8;
			
							controls.noZoom = false;
							controls.noPan = false;
			
							controls.staticMoving = true;
							controls.dynamicDampingFactor = 0.3;
			
							controls.keys = [ 65, 83, 68 ];
			
							controls.addEventListener( \'change\', render );
			
							// world
			
							scene = new THREE.Scene();
							scene.fog = new THREE.FogExp2( 0x000000, 0.002 );
											
											
											
							var binGeometry = new THREE.CubeGeometry( bin.size_1,bin.size_2,bin.size_3 );
							var binMaterial =  new THREE.MeshPhongMaterial( { color:0xffffff, shading: THREE.SmoothShading, wireframe: true } );
			
							var binMesh = new THREE.Mesh( binGeometry, binMaterial );
							binMesh.position.x = 0;
							binMesh.position.y = 0;
							binMesh.position.z = 0;
							binMesh.updateMatrix();
							binMesh.matrixAutoUpdate = false;
							scene.add( binMesh );
			
							for(var i=0; i < bin.items.length; ++i) {
								drawItems( scene, bin.items[i]);
							}
						   
						   
						   
							// lights
			
							ambientLight = new THREE.AmbientLight( 0x444444 );
							scene.add( ambientLight );
			
							pointLight = new THREE.PointLight( 0xffffff, 1.25, 1000 );
							pointLight.position.set( 0, 0, 600 );
			
							scene.add( pointLight );
			
							directionalLight = new THREE.DirectionalLight( 0xffffff );
							directionalLight.position.set( 1, -0.5, -1 );
							scene.add( directionalLight );
				   
			
							renderer = new THREE.WebGLRenderer( { antialias: false } );
							renderer.setClearColor( scene.fog.color, 1 );
							renderer.setSize( window.innerWidth, window.innerHeight );
			
							container = document.getElementById( \'container\' );
							container.innerHTML = "";
							container.appendChild( renderer.domElement );
			
							createLegend(container);
						   
							window.addEventListener( \'resize\', onWindowResize, false );
			
						}
									
					function drawItems(scene, item) {
						
						var is3sided = true;
						if( item.sp_size_3 == undefined) {
							
							item.sp_size_3 = 0.25;
							is3sided = false;
						}
						var itemGeometry = new THREE.CubeGeometry( item.sp_size_1, item.sp_size_2, item.sp_size_3 );
						
						var color = randomColor();
						
						itemColorHash[item.id + " : " + item.sp_size] = color;
						
						if( itemType == "normal")
							var itemMaterial =  new THREE.MeshPhongMaterial( { color:color, shading: THREE.SmoothShading } );
						else if ( itemType == "wireframe" )
							var itemMaterial =  new THREE.MeshPhongMaterial( { color:color, shading: THREE.SmoothShading, wireframe: true } );
						else if ( itemType == "transparent")
							var itemMaterial =  new THREE.MeshPhongMaterial( { color:color, shading: THREE.SmoothShading,transparent: true, opacity: 0.8 } );
							
						itemMaterial.name = item.id;
						var itemMesh = new THREE.Mesh( itemGeometry, itemMaterial );
						
						itemMesh.position.x = item.x_origin_in_bin;
						itemMesh.position.y = item.y_origin_in_bin;
						if(is3sided)
							itemMesh.position.z = item.z_origin_in_bin;
						
					  
					itemMesh.updateMatrix();
					itemMesh.matrixAutoUpdate = false;
					scene.add( itemMesh );
					
							
									 
				}
						
				
				function randomColor(){
					
					var color = \'#\'+Math.floor(Math.random()*16777215).toString(16);
							
					if( randomColorsUsedAlready[color] == true)
						randomColor();
					else
						randomColorsUsedAlready[color] = true;
						   
					return color;      
				}
				
				function createLegend(container) {
					var legend = document.createElement(\'div\');
					var table = document.createElement(\'table\');
					var headerrow = document.createElement(\'tr\');
					var headercell = document.createElement(\'td\');
					headercell.colSpan = 3;
					headercell.innerHTML = "contents legend";
					
					headerrow.appendChild(headercell);
					table.appendChild(headerrow);
					
					var hrrow = document.createElement(\'tr\');
					var hrcell = document.createElement(\'td\');
					hrcell.colSpan = 3;
					
					hrcell.appendChild(document.createElement(\'hr\'));
					hrrow.appendChild(hrcell);
					table.appendChild(hrrow);
					
					legend.appendChild(table);
					
					for (var key in itemColorHash) {
						if (itemColorHash.hasOwnProperty(key)) {
							
							var row = document.createElement(\'tr\');
							var key_cell = document.createElement(\'td\');
							var sep_cell = document.createElement(\'td\');
							var color_cell = document.createElement(\'td\');                
							
							key_cell.innerHTML = key;
							
							sep_cell.innerHTML = "=";
							
							
							var color_div = document.createElement(\'span\');
							color_div.style.height = \'10px\'
							color_div.style.width = \'10px\'
							color_div.style.background = itemColorHash[key];
							color_div.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
							
							color_cell.appendChild(color_div);
							
							row.appendChild(key_cell);
							row.appendChild(sep_cell);
							row.appendChild(color_cell);
							table.appendChild(row);
			
							  
							
						}
					}
					
					legend.style.position = \'absolute\';
					legend.style.top = \'100px\';
					legend.style.color = "#ffffff";
					legend.style.fontSize = "12px";
					legend.style.zIndex = 100;
						   
					container.appendChild( legend );
					
					
				}
			
				function onWindowResize() {
			
					camera.aspect = window.innerWidth / window.innerHeight;
					camera.updateProjectionMatrix();
			
					renderer.setSize( window.innerWidth, window.innerHeight );
			
					controls.handleResize();
			
					render();
			
				}
			
				function animate() {
			
					requestAnimationFrame( animate );
					controls.update();
			
				}
			
				function render() {
			
					renderer.render( scene, camera );
					//stats.update();
			
				}
			
			
					</script>
			
				</body>
			</html> `;*/


			