(function(){
	google.load('visualization', '1', { packages : ['controls'] } );
	google.setOnLoadCallback(function(){ 
	    angular.bootstrap(document.getElementById('player-app'), ['player-app']);
	});
	//const csv = require('csvtojson');
	var app = angular.module('player-app', []);

	app.controller('ctrl', ['$http', '$scope', function($http, $scope){
		$scope.loading = true;
		$http.get('/api/v1/fangraphs/pitching').then(function(data){
			$scope.loading = false;
            $scope.players = data.data;
        });
	    //$scope.players = [{"name": "Jameson Taillon", "pid": "11674"}, {"name": "Clayton Kershaw", "pid": "2036"}];

	    $scope.getPlayerData = function(selection){
	        console.log(selection.playerid);
	        $scope.loading = true;
	        $http.get('/api/v1/fangraphs/pitching/pitch-type/' + selection.playerid).then(function(data){
	            console.log(selection.playerid);
	            $scope.loading = false;
	            $scope.playerData = data.data;
	            $scope.drawPlot();
	        });
	    }
	    
	    $scope.drawPlot = function(){

			var g_data = new google.visualization.DataTable();
            g_data.addColumn('date', 'Time');
            g_data.addColumn('number', 'Fastball %');
            g_data.addColumn('number', 'Offspeed %');

            var data = $scope.playerData;
            var chart_data = [];
            var len = data.length;

            for (var i = 0; i < len; i+=1){
                var time = data[i].Date;
                var separators = [' ', '-', ':'];
                var p = time.split(new RegExp(separators.join('|'), 'g'));
                var date = new Date(p[0], p[1] - 1, p[2]);
                var a = [date, parseFloat(data[i]["Fastball %"]), parseFloat(data[i]["Breaking Ball %"])];
                chart_data.push(a);
            }
            g_data.addRows(chart_data);

            var chart = new google.visualization.ChartWrapper({
                'chartType': 'LineChart',
                'containerId': document.getElementById('chart'),
                'options': {
                	fontName: 'Noto Sans',
                	dataOpacity: 0.75,
                	backgroundColor: { fill: 'transparent' },
                	legend: {position: 'top'},
                	hAxis: {
                		title: 'Time',
                		textStyle: {
                    		fontSize: 12
                		}
                	},
                	vAxis: {
                		title: 'Pitch Type',
                		textStyle: {
                    		fontSize: 12
                		}
                	}
                }
            });

            var control = new google.visualization.ControlWrapper({
                'controlType': 'ChartRangeFilter',
                'containerId': 'control',
                'options': {
                    'filterColumnLabel': 'Time',
                    'ui': {
                    	chartOptions: {
                    		height: 25,
                    		backgroundColor: { fill: 'transparent' }
                    	},
                    	chartView: {
                    		columns: [0, {
                    			type: 'number',
                    			calc: function() {
                    				return 0;
                    			}
                    		}]
                    	}
                    }
                }
            });
            var dashboard = new google.visualization.Dashboard(document.getElementById('dashboard'));
            dashboard.bind(control, chart);
            dashboard.draw(g_data);
        };
	}]);
})();

		/*
		var p = document.getElementById("playerselect");
		var player = p.options[p.selectedIndex].text;
		console.log(player);
		var pid = "11674";
		$http.get('/api/v1/fangraphs/pitching/pitch-type/' + pid).then(function(rawData){
			$scope.$watch(function() {
		    	$('.selectpicker').selectpicker('refresh');
			});
			var arr = rawData.data;
			$scope.ptData = rawData.data;

			$scope.drawPlot = function(){

				var g_data = new google.visualization.DataTable();
	            g_data.addColumn('datetime', 'Time');
	            g_data.addColumn('number', 'Fastball %');
	            g_data.addColumn('number', 'Offspeed %');

	            var data = $scope.ptData;
	            var chart_data = [];
	            var len = data.length;

	            for (var i = 0; i < len; i+=1){
	                var time = data[i].Date;
	                var separators = [' ', '-', ':'];
	                var p = time.split(new RegExp(separators.join('|'), 'g'));
	                var date = new Date(p[0], p[1] - 1, p[2]);
	                var a = [date, parseFloat(data[i]["Fastball %"]), parseFloat(data[i]["Breaking Ball %"])];
	                chart_data.push(a);
	            }
	            g_data.addRows(chart_data);

	            var chart = new google.visualization.ChartWrapper({
	                'chartType': 'LineChart',
	                'containerId': document.getElementById('chart'),
	                'options': {
	                	fontName: 'Noto Sans',
	                	dataOpacity: 0.75,
	                	backgroundColor: { fill: 'transparent' },
	                	legend: {position: 'top'},
	                	hAxis: {
	                		title: 'Time',
	                		textStyle: {
	                    		fontSize: 12
	                		}
	                	},
	                	vAxis: {
	                		title: 'Pitch Type',
	                		textStyle: {
	                    		fontSize: 12
	                		}
	                	}
	                }
	            });

	            var control = new google.visualization.ControlWrapper({
	                'controlType': 'ChartRangeFilter',
	                'containerId': 'control',
	                'options': {
	                    'filterColumnLabel': 'Time',
	                    'ui': {
	                    	chartOptions: {
	                    		height: 25,
	                    		backgroundColor: { fill: 'transparent' }
	                    	},
	                    	chartView: {
	                    		columns: [0, {
	                    			type: 'number',
	                    			calc: function() {
	                    				return 0;
	                    			}
	                    		}]
	                    	}
	                    }
	                }
	            });
	            var dashboard = new google.visualization.Dashboard(document.getElementById('dashboard'));
	            dashboard.bind(control, chart);
	            dashboard.draw(g_data);
            };
		});
		*/
/*
	ptApp.$inject = ['$scope', 'PlayerService'];

	ptApp.factory('PlayerService', ['$http', '$q', function($http){
		var factory = {
			getPlayerData: function(player){
				console.log(player);
				var data = $http({method: 'GET', url: '/api/v1/fangraphs/pitching/pitch-type/' + player.pid});
				return data;
			}
		}
		return factory;
	}]);
*/