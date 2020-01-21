(function(){
	var app = angular.module('fp-app', []);

	app.controller('fp-ctrl', ['$http', '$scope', '$timeout', function($http, $scope, $timeout){

		$scope.getPages = function(data){
			var df = data.data;
			var len = data.data.length;
			var numPages = len / 20;
			var pages = [];
			for (var i = 0; i < numPages; i++){
				pages.push({'label': i+1, 'link': '', 'isActive': false});
			}
			return pages;
		};
		//$scope.getNHL = function(selection){
		$scope.loading = true;
		$http.get('/api/v1/corsica/skater_fp/FPG').then(function(data){
			//console.log(data.data);
			$scope.df = data;
			var df = data.data;
			var pages = $scope.getPages(data);
			pages[0].isActive = true;
			//console.log(len);
			$scope.pages = pages;
			$scope.players = df.slice(0, 20);
			$scope.loading = false;
			//console.log(angular.element("#fpTable")[0].offsetHeight);
			$timeout(function () {
		      $scope.hgt = $('#fpTable').height();
		      //console.log($scope.hgt);
		    }); 
		});

		

		$scope.gotoPage = function($event, data){
			var pageNum = parseInt($event.target.text);
			var start = (pageNum - 1) * 20;
			var end = (pageNum * 20);
			var df = data.data;
			var pages = $scope.getPages(data);

			pages[pageNum - 1].isActive = true;
			//console.log(len);
			$scope.pages = pages;
			
			//console.log(inx[0].label);
			$scope.players = df.slice(start, end);
			$timeout(function () {
		      $scope.hgt = $('#fpTable').height();
		      //console.log($scope.hgt);
		    }); 
		};

		$scope.gotoNext = function(pages, data){
			//var pageNum = parseInt($event.target.text);
			//console.log(pages);
			var pageArr = pages.filter(function(page){
				return page.isActive == true;
			});
			var pageNum = pageArr[0].label;
			if (pageNum < pages.length){
				var start = (pageNum) * 20;
				var end = (pageNum + 1) * 20;
				var df = data.data;
				//var pages = $scope.getPages(data);
				pages[pageNum - 1].isActive = false;
				pages[pageNum].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(start, end);
				$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			}
		};

		$scope.gotoPrev = function(pages, data){
			//console.log(pages);
			var pageArr = pages.filter(function(page){
				return page.isActive == true;
			});
			var pageNum = pageArr[0].label;
			//console.log(pageNum);
			if (pageNum > 1){
				var start = (pageNum - 2) * 20;
				var end = (pageNum - 1) * 20;
				var df = data.data;
				//var pages = $scope.getPages(data);
				pages[pageNum - 1].isActive = false;
				pages[pageNum - 2].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(start, end);
				$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			}
			
		};

	    $('.nfl').on('click', function() {
	    	$scope.loading = true;
	    	$('.nhl').removeClass('active');
	    	$('.mlb').removeClass('active');
	    	$('.nfl').addClass('active');
	    	var qb = $('.qb').attr('class');
	    	var rb = $('.rb').attr('class');
	    	var wr = $('.wr').attr('class');
	    	var te = $('.te').attr('class');
	    	var flex = $('.flex').attr('class');
    		var qbvalues = qb.split(" ");
    		var rbvalues = rb.split(" ");
    		var wrvalues = wr.split(" ");
    		var tevalues = te.split(" ");
    		var flexvalues = flex.split(" ");
    		if (qbvalues.pop() == 'active'){
    			var pos = 'QB';
    			var sort = 'FPG';
    			var sorted = 'FPGNFL';
    		}
    		if (rbvalues.pop() == 'active'){
    			var pos = 'RB';
    			var sort = 'WOG';
    			var sorted = 'WOG';
    		}
    		if (wrvalues.pop() == 'active'){
    			var pos = 'WR';
    			var sort = 'WOPRG';
    			var sorted = 'WOPRG';
    		}
    		if (tevalues.pop() == 'active'){
    			var pos = 'TE';
    			var sort = 'WOPRG';
    			var sorted = 'WOPRG';
    		}
    		if (flexvalues.pop() == 'active'){
    			var pos = 'flex';
    			var sort = 'WOG';
    			var sorted = 'WOG';
    		}
	    	$http.get('/api/v1/wopr/fp/' + pos + '/' + sort).then(function(data){
	    		$scope.df = data;
	    		var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$('.filters.nhl-options').removeClass('showx');
		    	$('.filters.nhl-options').addClass('hidex');
		    	$('.nhl-stats').removeClass('showx');
		    	$('.nhl-stats').addClass('hidex');
		    	$('.filters.mlb-options').removeClass('showx');
		    	$('.filters.mlb-options').addClass('hidex');
		    	$('.mlb-stats').removeClass('showx');
		    	$('.mlb-stats').addClass('hidex');
		    	$('.filters.nfl-options').removeClass('hidex');
		    	$('.filters.nfl-options').addClass('showx');
		    	$('.nfl-stats').removeClass('hidex');
		    	$('.nfl-stats').addClass('showx');
		    	$('table.showx th.sorted').removeClass('sorted');
	    		$('table.showx th#'+sorted.toLowerCase()).addClass('sorted');
	    		$('#fpgnfl').addClass('sorted');
		    	$scope.loading = false;
		    	$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});

	    });
	    $('.nhl').on('click', function() {
	    	$scope.loading = true;
	    	$('.nfl').removeClass('active');
	    	$('.mlb').removeClass('active');
	    	$('.nhl').addClass('active');
	    	var skater = $('.skater').attr('class');
    		var skatersplit = skater.split(" ");
    		if (skatersplit.pop() == 'active'){
    			var pos = 'skater_fp';
    		}
    		else{
    			var pos = 'goalie_fp';
    		}
	    	$http.get('/api/v1/corsica/' + pos + '/FPG').then(function(data){
	    		$scope.df = data;
	    		var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$('.filters.nfl-options').removeClass('showx');
		    	$('.filters.nfl-options').addClass('hidex');
		    	$('.nfl-stats').removeClass('showx');
		    	$('.nfl-stats').addClass('hidex');
		    	$('.filters.mlb-options').removeClass('showx');
		    	$('.filters.mlb-options').addClass('hidex');
		    	$('.mlb-stats').removeClass('showx');
		    	$('.mlb-stats').addClass('hidex');
		    	$('.filters.nhl-options').removeClass('hidex');
		    	$('.filters.nhl-options').addClass('showx');
		    	$('.nhl-stats').removeClass('hidex');
		    	$('.nhl-stats').addClass('showx');
		    	$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgnhl').addClass('sorted');
				$scope.loading = false;
				$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.mlb').on('click', function() {
	    	$scope.loading = true;
	    	$('.nhl').removeClass('active');
	    	$('.nfl').removeClass('active');
	    	$('.mlb').addClass('active');
	    	var batter = $('.batter').attr('class');
    		var battersplit = batter.split(" ");
    		if (battersplit.pop() == 'active'){
    			var pos = 'batter_fp';
    		}
    		else{
    			var pos = 'pitcher_fp';
    		}
	    	$http.get('/api/v1/sabr/' + pos + '/FPG').then(function(data){
	    		$scope.df = data;
	    		var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
		    	$('.filters.nhl-options').removeClass('showx');
		    	$('.filters.nhl-options').addClass('hidex');
		    	$('.nhl-stats').removeClass('showx');
		    	$('.nhl-stats').addClass('hidex');
		    	$('.filters.nfl-options').removeClass('showx');
		    	$('.filters.nfl-options').addClass('hidex');
		    	$('.nfl-stats').removeClass('showx');
		    	$('.nfl-stats').addClass('hidex');
		    	$('.filters.mlb-options').removeClass('hidex');
		    	$('.filters.mlb-options').addClass('showx');
		    	$('.mlb-stats').removeClass('hidex');
		    	$('.mlb-stats').addClass('showx');
		    	$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgmlb').addClass('sorted');
				$scope.loading = false;
				$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });

		$('.skater').on('click', function() {
			$scope.loading = true;
			$('.goalie').removeClass('active');
    		$('.skater').addClass('active');
			$http.get('/api/v1/corsica/skater_fp/FPG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgnhl').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
   		});
	    $('.goalie').on('click', function() {
	    	$scope.loading = true;
	    	$('.skater').removeClass('active');
    		$('.goalie').addClass('active');
	    	$http.get('/api/v1/corsica/goalie_fp/FPG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				//$scope.players = data.data;
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgnhl').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.qb').on('click', function() {
	    	$scope.loading = true;
	    	$('.rb').removeClass('active');
	    	$('.wr').removeClass('active');
	    	$('.te').removeClass('active');
	    	$('.flex').removeClass('active');
    		$('.qb').addClass('active');
	    	$http.get('/api/v1/wopr/fp/QB/FPG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgnfl').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.rb').on('click', function() {
	    	$scope.loading = true;
	    	$('.qb').removeClass('active');
	    	$('.wr').removeClass('active');
	    	$('.te').removeClass('active');
	    	$('.flex').removeClass('active');
    		$('.rb').addClass('active');
	    	$http.get('/api/v1/wopr/fp/RB/WOG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				console.log($scope.df);
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#wog').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.wr').on('click', function() {
	    	$scope.loading = true;
	    	$('.qb').removeClass('active');
	    	$('.rb').removeClass('active');
	    	$('.te').removeClass('active');
	    	$('.flex').removeClass('active');
    		$('.wr').addClass('active');
	    	$http.get('/api/v1/wopr/fp/WR/WOPRG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#woprg').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.te').on('click', function() {
	    	$scope.loading = true;
	    	$('.qb').removeClass('active');
	    	$('.rb').removeClass('active');
	    	$('.wr').removeClass('active');
	    	$('.flex').removeClass('active');
    		$('.te').addClass('active');
	    	$http.get('/api/v1/wopr/fp/TE/WOPRG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#woprg').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.flex').on('click', function() {
	    	$scope.loading = true;
	    	//var newcol = $(this);
	    	$('.qb').removeClass('active');
	    	$('.rb').removeClass('active');
	    	$('.wr').removeClass('active');
	    	$('.te').removeClass('active');
    		$('.flex').addClass('active');
	    	$http.get('/api/v1/wopr/fp/flex/WOG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#wog').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });
	    $('.batter').on('click', function() {
			$scope.loading = true;
			$('.pitcher').removeClass('active');
    		$('.batter').addClass('active');
			$http.get('/api/v1/SABR/batter_fp/FPG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgmlb').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
   		});
	    $('.pitcher').on('click', function() {
	    	$scope.loading = true;
	    	$('.batter').removeClass('active');
    		$('.pitcher').addClass('active');
	    	$http.get('/api/v1/SABR/pitcher_fp/FPG').then(function(data){
				//console.log(data.data);
				$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				//$scope.players = data.data;
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		$('#fpgmlb').addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
	    });

	    $('.sortable').on('click', function() {
	    	$scope.loading = true;
	    	var newcol = $(this);
	    	var sport = $('ul#sport-filters > li.active').text().toLowerCase();
	    	//console.log(sport);
	    	var pos_base = $('div.showx > ul#filters > li.active').text().toLowerCase();
	    	//console.log(pos_base);
	    	var pos = '';
	    	if (sport == 'nhl'){
	    		api = 'corsica';
	    		pos = pos_base + '_fp';
	    	}
	    	if (sport == 'nfl'){
	    		api = 'wopr';
	    		pos = 'fp/' + pos_base.toUpperCase();
	    	}
	    	if (sport == 'mlb'){
	    		api = 'sabr';
	    		pos = pos_base + '_fp';
	    	}
	    	//console.log(sport);
	    	var sort = $(this).text().replace('/', '');
	    	$http.get('/api/v1/' + api + '/' + pos + '/' + sort).then(function(data){
	    		$scope.df = data;
				var df = data.data;
				var pages = $scope.getPages(data);
				pages[0].isActive = true;
				//console.log(len);
				$scope.pages = pages;
				$scope.players = df.slice(0, 20);
				$scope.loading = false;
				$('table.showx th.sorted').removeClass('sorted');
	    		//console.log($(this));
	    		newcol.addClass('sorted');
	    		$timeout(function () {
			      $scope.hgt = $('#fpTable').height();
			      //console.log($scope.hgt);
			    }); 
			});
			
	    })

		//}
	}]);

	angular.bootstrap(document.getElementById('fp-app'), ['fp-app']);
})();