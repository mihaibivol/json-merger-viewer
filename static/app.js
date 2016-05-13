var app = angular.module('diffApp', ['ds.objectDiff', 'ngSanitize']);

app.directive('mergeView', function() {
    var controller = function($scope, ObjectDiff) {
        $scope.rootHeadDiff = ObjectDiff.diff($scope.mergeInfo.rhRoot,
                                              $scope.mergeInfo.rhHead)
        $scope.rootUpdateDiff = ObjectDiff.diff($scope.mergeInfo.ruRoot,
                                                $scope.mergeInfo.ruUpdate)
        $scope.headMergedDiff = ObjectDiff.diff($scope.mergeInfo.hmHead,
                                                $scope.mergeInfo.hmMerged)
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
