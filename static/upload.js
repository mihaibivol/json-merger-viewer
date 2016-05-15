var app = angular.module('uploadApp', []);

app.directive('uploadForm', function() {
    var controller = function($scope) {
        $scope.provideRoot = true;
        $scope.rootURL = true;
        $scope.headURL = true;
        $scope.updateURL = true;

        $scope.toggle = function(field) {
            $scope[field] = !$scope[field];
        };

        $scope.setRootURL = function() {
            $scope.provideRoot = true;
            $scope.rootURL = true;
        };

        $scope.setRootUpload = function() {
            $scope.provideRoot = true;
            $scope.rootURL = false;
        };

        $scope.setRootNone = function() {
            $scope.provideRoot = false;
        };

        $scope.isRootURL = function() {
            return $scope.provideRoot && $scope.rootURL;
        };

        $scope.isRootUpload = function() {
            return $scope.provideRoot && !$scope.rootURL;
        };

        $scope.isRootNone = function() {
            return !$scope.provideRoot;
        };
    };

    return {
        'restrict': 'E',
        'scope': {
            'template': '@',
            'action': '@'
        },
        'controller': controller,
        'template': '<div ng-include="template"></div>'
    };
});
