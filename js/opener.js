(function(){
	var app = angular.module('opener-app', []);

	app.controller('opener-ctrl', ['$http', '$scope', function($http, $scope){
		$scope.tbl = false;
		
		$http.get('/api/v1/sabr/teams').then(function(data){
			$scope.teamData = data.data;
			$scope.teams = data.data.map(function (el) { 
				return el.master_abbr; 
			});
        });

        $scope.get_candidate_data = function(data){
        	var p_data = data.data
    		var pitchers = [];
    		if (p_data.length == 0){
    			pitchers.push({"name": "N/A", "wOBA": "N/A"});
    		}
    		for (var i = 0; i < p_data.length; i++){
    			var player = p_data[i];
    			pitchers.push({"name": player['Player'], "wOBA": player['wOBA']});
    		}
    		return pitchers;
        }

	    $scope.getCandidates = function(selection){
	    	data = $scope.teamData;
	    	console.log(selection);
	    	$scope.loading = true;

		    $http.get('/api/v1/sabr/teams').then(function(data){
		    	for (var i = 0; i < data.data.length; i++){
		    		if (data.data[i].master_abbr == selection || data.data[i].team == selection){
		    			console.log(data.data[i]);
		    			var sa_abbr = data.data[i].abbrs[0].sa;
		    			var bref_abbr = data.data[i].abbrs[0].bref;
		    			var master_abbr = data.data[i].master_abbr;
		    			$scope.teamName = data.data[i].full_name[0];
		    			console.log(sa_abbr);
		    			console.log(bref_abbr);
		    			$http.get('/api/v1/sabr/opener/' + master_abbr).then(function(data){
				    		var chunkData = data.data;
				    		$scope.chunk = chunkData;
				            $scope.tbl = true;
				            if (sa_abbr == 'ANY'){
					        	$scope.desc = false;
					        }
					        else{
					        	$scope.desc = true;
					        }
					        $http.get('/api/v1/sabr/opener/' + sa_abbr + '/RP/R').then(function(data){
					    		$scope.rrps = $scope.get_candidate_data(data);
				    			$http.get('/api/v1/sabr/opener/' + sa_abbr + '/SP/R').then(function(data){
						    		$scope.rsps = $scope.get_candidate_data(data);
						    		$http.get('/api/v1/sabr/opener/' + sa_abbr + '/RP/L').then(function(data){
							    		$scope.lrps = $scope.get_candidate_data(data);
							    		$http.get('/api/v1/sabr/opener/' + sa_abbr + '/SP/L').then(function(data){
								    		$scope.lsps = $scope.get_candidate_data(data);
								    		$scope.loading = false;
				    					});
				    				});
				    			});
				    		});
				    	});
		    		}
		    	}
		    });
	    }
	}]);

	angular.bootstrap(document.getElementById('opener-app'), ['opener-app']);
})();