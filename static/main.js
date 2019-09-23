(function () {

  'use strict';

  angular.module('JobViewerApp', [])

  .controller('JobViewerController', ['$scope', '$log', '$http', '$timeout',
    function($scope, $log, $http, $timeout) {

    $scope.submitButtonText = 'Submit';
    $scope.loading = false;
    $scope.urlerror = false;

    $scope.getResults = function() {


      // get the URL from the input
      var userInput = $scope.url;
      var job = $scope.job
      // fire the API request
      $http.post('/start', {'url': userInput, 'job': job}).
        success(function(results) {
          getJobInfo(results);
          $scope.wordcounts = null;
          $scope.loading = true;
          $scope.submitButtonText = 'Loading...';
          $scope.urlerror = false;
        }).
        error(function(error) {
          $log.log(error);
        });

    };

    function getJobInfo(jobID) {

      var timeout = '';
      var poller = function() {
        // fire another request
        $http.get('/results/'+jobID).
          success(function(data, status, headers, config) {
            if(status === 202) {
              $log.log(data, status);
            } else if (status === 200){
              $scope.loading = false;
              $scope.submitButtonText = "Submit";
              $scope.jobdata = data;
              $timeout.cancel(timeout);
              return false;
            }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            timeout = $timeout(poller, 2000);
          }).
          error(function(error) {
            $log.log(error);
            $scope.loading = false;
            $scope.submitButtonText = "Submit";
            $scope.urlerror = true;
          });
      };

      poller();
    }

  }])

}());
