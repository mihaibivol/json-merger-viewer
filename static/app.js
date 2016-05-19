var app = angular.module('diffApp', ['ds.objectDiff', 'ngSanitize']);

app.directive('mergeView', function() {
    var controller = function($scope, $location, $anchorScroll, ObjectDiff) {
        $scope.rootHeadDiff = ObjectDiff.diff($scope.mergeInfo.rhRoot,
                                              $scope.mergeInfo.rhHead)
        $scope.rootUpdateDiff = ObjectDiff.diff($scope.mergeInfo.ruRoot,
                                                $scope.mergeInfo.ruUpdate)
        $scope.headMergedDiff = ObjectDiff.diff($scope.mergeInfo.hmHead,
                                                $scope.mergeInfo.hmMerged)
        $scope.scrollTo = function(id) {
            if ($location.hash() !== id) {
                $location.hash(id);
            } else {
                $anchorScroll();
            }
        }

        $scope.colClass = 'col-md-6';
        $scope.fullDiff = true;
        $scope.showOrig = true;

        $scope.setMode = function(mode) {
            if (mode == 'sbs') {
                $scope.colClass = 'col-md-6';
                $scope.fullDiff = true;
                $scope.showOrig = true;
            } else if (mode == 'min') {
                $scope.colClass = 'col-md-12';
                $scope.fullDiff = false;
                $scope.showOrig = false;
            } else if (mode == 'full') {
                $scope.colClass = 'col-md-12';
                $scope.fullDiff = true;
                $scope.showOrig = false;
            }
        }
    };

    return {
        'restrict': 'E',
        'scope': {
            'mergeInfo': '=',
            'template': '@'
        },
        'controller': controller,
        'template': '<div ng-include="template"></div>'
    };
});
